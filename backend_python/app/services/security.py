import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any


JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))


def hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), password_salt.encode(), 120_000)
    return f"{password_salt}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, expected = password_hash.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), f"{salt}${expected}")


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _sign(value: str) -> str:
    signature = hmac.new(JWT_SECRET.encode(), value.encode(), hashlib.sha256).digest()
    return _b64encode(signature)


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": int((datetime.now(timezone.utc) + expires_delta).timestamp()),
    }
    body = _b64encode(json.dumps(payload).encode())
    unsigned = f"{header}.{body}"
    return f"{unsigned}.{_sign(unsigned)}"


def create_access_token(subject: str) -> str:
    return create_token(subject, "access", timedelta(minutes=ACCESS_TOKEN_MINUTES))


def create_refresh_token(subject: str) -> str:
    return create_token(subject, "refresh", timedelta(days=REFRESH_TOKEN_DAYS))


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    try:
        header, body, signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Malformed token") from exc

    unsigned = f"{header}.{body}"
    if not hmac.compare_digest(_sign(unsigned), signature):
        raise ValueError("Invalid token signature")

    padding = "=" * (-len(body) % 4)
    payload = json.loads(base64.urlsafe_b64decode(f"{body}{padding}").decode())
    if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Expired token")
    if expected_type and payload.get("type") != expected_type:
        raise ValueError("Wrong token type")
    return payload
