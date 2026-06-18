from fastapi import APIRouter, File, UploadFile

from app.models.submission import FormTypeUpdate, PaymentUpdate, Presenter, Submission, SubmissionCreate, SubmitUpdate
from app.services import submission_service

router = APIRouter(prefix="/bp-api/submission", tags=["submissions"])


@router.post("/new", response_model=Submission)
def create_submission(payload: SubmissionCreate) -> Submission:
    return submission_service.create_submission(payload)


@router.put("/{submission_id}/payment", response_model=Submission)
def update_payment(submission_id: str, payload: PaymentUpdate) -> Submission:
    return submission_service.update_payment(submission_id, payload)


@router.put("/{submission_id}/presenter", response_model=Submission)
def update_presenter(submission_id: str, payload: Presenter) -> Submission:
    return submission_service.update_presenter(submission_id, payload)


@router.put("/{submission_id}/formType", response_model=Submission)
def update_form_type(submission_id: str, payload: FormTypeUpdate) -> Submission:
    return submission_service.update_form_type(submission_id, payload)


@router.put("/{submission_id}/files", response_model=Submission)
async def add_file(submission_id: str, file: UploadFile = File(...)) -> Submission:
    return await submission_service.add_file(submission_id, file)


@router.put("/{submission_id}", response_model=Submission)
def submit(submission_id: str, payload: SubmitUpdate) -> Submission:
    return submission_service.submit(submission_id, payload)


@router.get("/{submission_id}", response_model=Submission)
def get_submission(submission_id: str) -> Submission:
    return submission_service.get_submission_or_404(submission_id)
