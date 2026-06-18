import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.models.submission import FileDetails, QueueFileResponse, Submission

try:
    import boto3
except ImportError:  # pragma: no cover - optional runtime dependency
    boto3 = None


AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
S3_BUCKET = os.getenv("S3_BUCKET", "bp-submission-files")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "bp-submission-conversion-queue")
LOCAL_FILE_DIR = Path(os.getenv("LOCAL_FILE_DIR", "/tmp/bp-bedrock-service/files"))
LOCAL_FILE_DIR.mkdir(parents=True, exist_ok=True)


def _client(service_name: str):
    if boto3 is None:
        return None
    if os.getenv("USE_AWS_SERVICES", "false").lower() != "true" and not AWS_ENDPOINT_URL:
        return None
    kwargs = {"region_name": AWS_REGION}
    if AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = AWS_ENDPOINT_URL
    return boto3.client(service_name, **kwargs)


async def store_pdf(submission_id: str, upload: UploadFile) -> FileDetails:
    content = await upload.read()
    file_id = str(uuid4())
    safe_name = Path(upload.filename or "submission.pdf").name
    s3_key = f"submissions/{submission_id}/source/{file_id}-{safe_name}"

    s3_client = _client("s3")
    if s3_client:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=content,
            ContentType=upload.content_type or "application/pdf",
        )
    else:
        target = LOCAL_FILE_DIR / s3_key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    return FileDetails(
        form_id=file_id,
        file_name=safe_name,
        file_size=len(content),
        original_file_id=file_id,
        original_s3_key=s3_key,
    )


def queue_submission_file(submission: Submission, file_details: FileDetails) -> QueueFileResponse:
    target_key = f"submissions/{submission.id}/converted/{file_details.form_id}.tiff"
    message = {
        "submission_id": submission.id,
        "file_id": file_details.form_id,
        "source_s3_key": file_details.original_s3_key,
        "target_s3_key": target_key,
        "bucket": S3_BUCKET,
    }

    sqs_client = _client("sqs")
    if sqs_client and SQS_QUEUE_URL:
        result = sqs_client.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(message))
        return QueueFileResponse(
            queued=True,
            message_id=result.get("MessageId"),
            detail="File queued for conversion",
        )

    local_queue = LOCAL_FILE_DIR.parent / "queue.jsonl"
    with local_queue.open("a", encoding="utf-8") as queue_file:
        queue_file.write(json.dumps(message) + "\n")
    return QueueFileResponse(queued=True, message_id=None, detail="File queued locally for conversion")
