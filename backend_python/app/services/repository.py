import json
import os
from pathlib import Path
from typing import Any

from app.models.submission import Submission, UserRecord

try:
    import boto3
except ImportError:  # pragma: no cover - optional runtime dependency
    boto3 = None


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

    def upsert_submission(self, submission: Submission) -> Submission:
        self.submissions.put_item(Item=submission.model_dump(mode="json"))
        return submission

    def get_submission(self, submission_id: str) -> Submission | None:
        response = self.submissions.get_item(Key={"id": submission_id})
        item = response.get("Item")
        return Submission.model_validate(item) if item else None


def _build_repository() -> Repository:
    if os.getenv("USE_DYNAMODB", "false").lower() == "true":
        return DynamoDbRepository()
    return LocalJsonRepository()


repository = _build_repository()
