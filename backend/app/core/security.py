import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16_384,
        r=8,
        p=1,
    )
    return "scrypt${}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt_text, digest_text = stored_hash.split("$", 2)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16_384, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _secret() -> bytes:
    configured = get_settings().auth_secret_key
    if configured:
        return configured.encode("utf-8")
    # Local development works without a secret file; production must set one.
    if not hasattr(_secret, "generated"):
        _secret.generated = secrets.token_bytes(32)  # type: ignore[attr-defined]
    return _secret.generated  # type: ignore[attr-defined]


def create_session_token(user_id: int) -> str:
    payload = {"user_id": user_id, "expires_at": int(time.time()) + 60 * 60 * 24 * 7}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def read_session_token(token: str) -> int | None:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(encoded.encode("ascii")))
        if int(payload["expires_at"]) < int(time.time()):
            return None
        return int(payload["user_id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
