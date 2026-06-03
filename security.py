from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

from config import settings

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)


def create_token(email: str) -> str:
    cfg = settings()
    payload = {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=cfg.token_minutes)}
    return jwt.encode(payload, cfg.secret_key, algorithm=cfg.algorithm)


def read_token(token: str) -> str | None:
    try:
        return jwt.decode(token, settings().secret_key, algorithms=[settings().algorithm]).get("sub")
    except JWTError:
        return None
