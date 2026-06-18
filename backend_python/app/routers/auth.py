from fastapi import APIRouter, HTTPException

from app.models.submission import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRecord,
    utc_now,
)
from app.services.repository import repository
from app.services.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/bp-api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate) -> TokenResponse:
    user = UserRecord(
        email=payload.email,
        display_name=payload.display_name,
        timezone=payload.timezone,
        password_hash=hash_password(payload.password),
    )
    try:
        repository.create_user(user)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _tokens(user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin) -> TokenResponse:
    user = repository.get_user_by_email(str(payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _tokens(user.email)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: dict[str, str]) -> TokenResponse:
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token is required")
    try:
        decoded = decode_token(token, "refresh")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return _tokens(decoded["sub"])


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest) -> dict[str, str]:
    return {"status": "ok", "detail": f"Password reset requested for {payload.email}"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest) -> dict[str, str]:
    user = repository.get_user_by_email(str(payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(payload.new_password)
    user.last_updated_at = utc_now()
    repository.upsert_user(user)
    return {"status": "ok"}


def _tokens(email: str) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(email), refresh_token=create_refresh_token(email))
