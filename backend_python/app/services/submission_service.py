from fastapi import HTTPException, UploadFile

from app.models.submission import (
    ConversionStatus,
    ConvertedFileUpdate,
    FileDetails,
    FormTypeUpdate,
    PaymentUpdate,
    Presenter,
    QueueFileResponse,
    Submission,
    SubmissionCreate,
    SubmissionStatus,
    SubmitUpdate,
    utc_now,
)
from app.services import aws_service
from app.services.repository import repository


def create_submission(payload: SubmissionCreate) -> Submission:
    submission = Submission(presenter=payload.presenter)
    return repository.upsert_submission(submission)


def get_submission_or_404(submission_id: str) -> Submission:
    submission = repository.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


def update_presenter(submission_id: str, payload: Presenter) -> Submission:
    submission = get_submission_or_404(submission_id)
    submission.presenter = payload
    submission.last_modified_at = utc_now()
    return repository.upsert_submission(submission)


def update_payment(submission_id: str, payload: PaymentUpdate) -> Submission:
    submission = get_submission_or_404(submission_id)
    submission.payment_reference = payload.payment_reference
    submission.last_modified_at = utc_now()
    return repository.upsert_submission(submission)


def update_form_type(submission_id: str, payload: FormTypeUpdate) -> Submission:
    submission = get_submission_or_404(submission_id)
    submission.form.form_type = payload.form_type
    submission.last_modified_at = utc_now()
    return repository.upsert_submission(submission)


async def add_file(submission_id: str, upload: UploadFile) -> Submission:
    if upload.content_type not in {"application/pdf", "application/octet-stream", None}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")
    submission = get_submission_or_404(submission_id)
    file_details = await aws_service.store_pdf(submission_id, upload)
    submission.form.file_details.append(file_details)
    submission.last_modified_at = utc_now()
    return repository.upsert_submission(submission)


def update_file_conversion(submission_id: str, file_id: str, payload: ConvertedFileUpdate) -> Submission:
    submission = get_submission_or_404(submission_id)
    file_details = _get_file_or_404(submission, file_id)
    file_details.converted_file_id = payload.converted_file_id
    file_details.converted_s3_key = payload.converted_s3_key
    file_details.conversion_status = payload.conversion_status
    file_details.last_modified_at = utc_now()
    submission.last_modified_at = utc_now()
    return repository.upsert_submission(submission)


def submit(submission_id: str, payload: SubmitUpdate) -> Submission:
    submission = get_submission_or_404(submission_id)
    if payload.status != SubmissionStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Only SUBMITTED is accepted for MVP submit")
    if not submission.presenter.email or not submission.payment_reference or not submission.form.form_type:
        raise HTTPException(status_code=400, detail="Presenter, payment, and form type are required")
    if not submission.form.file_details:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")

    submission.status = SubmissionStatus.SUBMITTED
    submission.last_modified_at = utc_now()
    for file_details in submission.form.file_details:
        if file_details.conversion_status == ConversionStatus.WAITING:
            file_details.conversion_status = ConversionStatus.QUEUED
            file_details.last_modified_at = utc_now()
    submission = repository.upsert_submission(submission)
    for file_details in submission.form.file_details:
        aws_service.queue_submission_file(submission, file_details)
    return submission


def queue_file(submission_id: str, file_id: str) -> QueueFileResponse:
    submission = get_submission_or_404(submission_id)
    file_details = _get_file_or_404(submission, file_id)
    file_details.conversion_status = ConversionStatus.QUEUED
    file_details.last_modified_at = utc_now()
    repository.upsert_submission(submission)
    return aws_service.queue_submission_file(submission, file_details)


def _get_file_or_404(submission: Submission, file_id: str) -> FileDetails:
    for file_details in submission.form.file_details:
        if file_details.form_id == file_id:
            return file_details
    raise HTTPException(status_code=404, detail="File not found")
