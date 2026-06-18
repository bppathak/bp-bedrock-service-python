from fastapi import APIRouter

from app.models.submission import FormsResponse

router = APIRouter(prefix="/bp-api", tags=["forms"])


@router.get("/forms", response_model=FormsResponse)
def get_forms() -> FormsResponse:
    return FormsResponse(
        forms=[
            {"id": "passport", "name": "Passport application"},
            {"id": "visa", "name": "Visa application"},
            {"id": "benefits", "name": "Benefits claim"},
        ]
    )
