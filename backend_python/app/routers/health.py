from fastapi import APIRouter

router = APIRouter(prefix="/bp-api", tags=["health"])


@router.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
