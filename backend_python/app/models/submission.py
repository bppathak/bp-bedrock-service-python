from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SubmissionStatus(StrEnum):
    OPEN = "OPEN"
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    SENT_TO_EXTERNALSYSTEM = "SENT_TO_EXTERNALSYSTEM"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ConversionStatus(StrEnum):
    WAITING = "WAITING"
    QUEUED = "QUEUED"
    CONVERTED = "CONVERTED"
    FAILED = "FAILED"


class Presenter(BaseModel):
    email: EmailStr
    display_name: str | None = None
    phone: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str
    timezone: str = "UTC"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(min_length=8)


class UserRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    password_hash: str
    display_name: str
    timezone: str = "UTC"
    create_at: datetime = Field(default_factory=utc_now)
    last_updated_at: datetime = Field(default_factory=utc_now)


class PaymentUpdate(BaseModel):
    payment_reference: str


class FormTypeUpdate(BaseModel):
    form_type: str


class SubmissionCreate(BaseModel):
    presenter: Presenter


class FileDetails(BaseModel):
    form_id: str = Field(default_factory=lambda: str(uuid4()))
    file_name: str
    file_size: int
    original_file_id: str | None = None
    original_s3_key: str | None = None
    converted_file_id: str | None = None
    converted_s3_key: str | None = None
    conversion_status: ConversionStatus = ConversionStatus.WAITING
    last_modified_at: datetime = Field(default_factory=utc_now)


class FileMetadataUpdate(BaseModel):
    file_name: str
    file_size: int
    original_file_id: str | None = None
    original_s3_key: str | None = None


class ConvertedFileUpdate(BaseModel):
    converted_file_id: str
    converted_s3_key: str
    conversion_status: ConversionStatus = ConversionStatus.CONVERTED


class SubmissionForm(BaseModel):
    form_type: str | None = None
    file_details: list[FileDetails] = Field(default_factory=list)


class Submission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    create_at: datetime = Field(default_factory=utc_now)
    last_modified_at: datetime = Field(default_factory=utc_now)
    status: SubmissionStatus = SubmissionStatus.OPEN
    presenter: Presenter
    payment_reference: str | None = None
    form: SubmissionForm = Field(default_factory=SubmissionForm)


class SubmitUpdate(BaseModel):
    status: SubmissionStatus = SubmissionStatus.SUBMITTED


class FormsResponse(BaseModel):
    forms: list[dict[str, Any]]


class QueueFileRequest(BaseModel):
    submission_id: str
    file_id: str


class QueueFileResponse(BaseModel):
    queued: bool
    message_id: str | None = None
    detail: str
