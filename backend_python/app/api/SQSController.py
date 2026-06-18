from fastapi import APIRouter

from app.models.SQSModel import SQSRequest, SQSResponse

router = APIRouter(prefix="/sqs", tags=["legacy-sqs"])


@router.post("/health")
def health_check() -> dict[str, str]:
    return {"status": "Service running ok"}


@router.post("/sendMessage", response_model=SQSResponse)
def send_message(sqs_request: SQSRequest) -> SQSResponse:
    return SQSResponse(userResponse=f"Legacy SQS endpoint received: {sqs_request.message}")
