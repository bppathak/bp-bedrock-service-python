from fastapi import APIRouter

from app.models.submission import QueueFileRequest, QueueFileResponse
from app.services import submission_service

router = APIRouter(prefix="/bp-api", tags=["queue"])


@router.post("/queue-file", response_model=QueueFileResponse)
def queue_file(payload: QueueFileRequest) -> QueueFileResponse:
    return submission_service.queue_file(payload.submission_id, payload.file_id)
