from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from app.resources.config import settings
from app.schemas.token import TokenData

SECRET_KEY = settings.jwt_secret_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_username_from_token(token: str, secret_key: str) -> str:
    try:
        return TokenData(**jwt.decode(token, secret_key, algorithms=[ALGORITHM])).username
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
