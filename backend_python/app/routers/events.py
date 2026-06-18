from fastapi import APIRouter

from app.models.submission import ConvertedFileUpdate, Submission
from app.services import submission_service

router = APIRouter(prefix="/bp-api/events", tags=["events"])


@router.post("/submissions/{submission_id}/files/{file_id}", response_model=Submission)
def update_converted_file(
    submission_id: str,
    file_id: str,
    payload: ConvertedFileUpdate,
) -> Submission:
    return submission_service.update_file_conversion(submission_id, file_id, payload)
