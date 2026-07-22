import json
import os
import logging
from pathlib import Path
from typing import Any
from datetime import datetime

from app.models.submission import Submission, UserRecord
from botocore.exceptions import ClientError

try:
    import boto3
except ImportError:  # pragma: no cover - optional runtime dependency
    boto3 = None

logger = logging.getLogger(__name__)


class Repository:
    def create_user(self, user: UserRecord) -> UserRecord:
        raise NotImplementedError

    def upsert_user(self, user: UserRecord) -> UserRecord:
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> UserRecord | None:
        raise NotImplementedError

    def upsert_submission(self, submission: Submission) -> Submission:
        raise NotImplementedError

    def get_submission(self, submission_id: str) -> Submission | None:
        raise NotImplementedError


class LocalJsonRepository(Repository):
    def __init__(self) -> None:
        data_dir = Path(os.getenv("LOCAL_DATA_DIR", "/tmp/bp-bedrock-service"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "db.json"
        if not self.path.exists():
            self.path.write_text(json.dumps({"users": {}, "submissions": {}}), encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")

    def create_user(self, user: UserRecord) -> UserRecord:
        data = self._read()
        if str(user.email).lower() in data["users"]:
            raise ValueError("Email already registered")
        data["users"][str(user.email).lower()] = user.model_dump(mode="json")
        self._write(data)
        return user

    def upsert_user(self, user: UserRecord) -> UserRecord:
        data = self._read()
        data["users"][str(user.email).lower()] = user.model_dump(mode="json")
        self._write(data)
        return user

    def get_user_by_email(self, email: str) -> UserRecord | None:
        data = self._read()
        item = data["users"].get(email.lower())
        return UserRecord.model_validate(item) if item else None

    def upsert_submission(self, submission: Submission) -> Submission:
        data = self._read()
        data["submissions"][submission.id] = submission.model_dump(mode="json")
        self._write(data)
        return submission

    def get_submission(self, submission_id: str) -> Submission | None:
        data = self._read()
        item = data["submissions"].get(submission_id)
        return Submission.model_validate(item) if item else None


class DynamoDbRepository(Repository):
    def __init__(self) -> None:
        if boto3 is None:
            raise RuntimeError("boto3 is required when USE_DYNAMODB=true")
        kwargs = {
            "endpoint_url": os.getenv("AWS_ENDPOINT_URL"),
            "region_name": os.getenv("AWS_DEFAULT_REGION", "eu-west-2"),
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        }
        endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        resource = boto3.resource("dynamodb", **kwargs)
        self.users = resource.Table(os.getenv("DYNAMODB_USERS_TABLE", "bp-users"))
        self.submissions = resource.Table(os.getenv("DYNAMODB_SUBMISSIONS_TABLE", "bp-submissions"))

    def create_user(self, user: UserRecord) -> UserRecord:
        if self.get_user_by_email(str(user.email)):
            raise ValueError("Email already registered")
        return self.upsert_user(user)

    def upsert_user(self, user: UserRecord) -> UserRecord:
        item = user.model_dump(mode="json")
        item["email"] = str(user.email).lower()
        self.users.put_item(Item=item)
        return user

    def get_user_by_email(self, email: str) -> UserRecord | None:
        response = self.users.get_item(Key={"email": email.lower()})
        item = response.get("Item")
        return UserRecord.model_validate(item) if item else None

    def _serialize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Convert Pydantic model to DynamoDB-compatible format.
        
        Handles serialization of datetime objects and nested structures
        to ensure compatibility with DynamoDB put_item operations.
        """
        serialized = {}
        for key, value in item.items():
            if isinstance(value, datetime):
                # Convert datetime to ISO format string for DynamoDB
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                # Recursively serialize nested dictionaries
                serialized[key] = self._serialize_item(value)
            elif isinstance(value, list):
                # Handle lists with datetime or nested objects
                serialized[key] = [
                    self._serialize_item(v) if isinstance(v, dict) 
                    else v.isoformat() if isinstance(v, datetime) 
                    else v
                    for v in value
                ]
            elif value is None:
                # Skip None values as DynamoDB doesn't store them
                continue
            else:
                serialized[key] = value
        return serialized

    def upsert_submission(self, submission: Submission) -> Submission:
        """Upsert submission with proper serialization and error handling for DynamoDB.
        
        This method handles:
        - Conversion of Pydantic datetime objects to ISO format strings
        - Nested object serialization (Presenter, SubmissionForm)
        - DynamoDB-specific type constraints
        - Comprehensive error logging for Red Hat Linux environments
        
        Args:
            submission: Submission model instance to upsert
            
        Returns:
            Submission: The upserted submission object
            
        Raises:
            ClientError: If DynamoDB operation fails
            Exception: For unexpected errors during serialization
        """
        try:
            # Convert Pydantic model to dictionary
            item = submission.model_dump(mode="json")
            
            # Serialize all datetime objects and nested structures for DynamoDB compatibility
            item = self._serialize_item(item)
            
            # Add metadata for audit trails
            item["_updated_at"] = datetime.utcnow().isoformat()
            item["_environment"] = os.getenv("ENVIRONMENT", "production")
            
            logger.debug(
                f"Preparing to upsert submission: {submission.id}",
                extra={"submission_id": submission.id}
            )
            
            # Put item into DynamoDB table
            self.submissions.put_item(Item=item)
            
            logger.info(
                "Submission upserted successfully",
                extra={
                    "submission_id": submission.id,
                    "presenter_email": submission.presenter.email,
                    "status": submission.status,
                    "form_type": submission.form.form_type
                }
            )
            return submission
            
        except ClientError as e:
            # Handle AWS/DynamoDB-specific errors
            error_code = e.response.get("Error", {}).get("Code", "UNKNOWN")
            error_message = e.response.get("Error", {}).get("Message", "No message provided")
            
            logger.error(
                f"DynamoDB submission upsert failed: {error_code}",
                extra={
                    "submission_id": submission.id,
                    "error_code": error_code,
                    "error_message": error_message,
                    "exception_type": type(e).__name__
                },
                exc_info=True
            )
            raise
        except TypeError as e:
            # Handle serialization type errors
            logger.error(
                "Type error during submission serialization",
                extra={
                    "submission_id": submission.id,
                    "error_message": str(e),
                    "exception_type": "TypeError"
                },
                exc_info=True
            )
            raise ValueError(f"Failed to serialize submission: {str(e)}") from e
        except Exception as e:
            # Catch any unexpected errors
            logger.error(
                "Unexpected error during submission upsert",
                extra={
                    "submission_id": submission.id,
                    "exception_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )
            raise

    def get_submission(self, submission_id: str) -> Submission | None:
        response = self.submissions.get_item(Key={"id": submission_id})
        item = response.get("Item")
        return Submission.model_validate(item) if item else None


def _build_repository() -> Repository:
    if os.getenv("USE_DYNAMODB", "false").lower() == "true":
        return DynamoDbRepository()
    return LocalJsonRepository()


repository = _build_repository()