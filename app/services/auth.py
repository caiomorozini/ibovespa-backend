from fastapi.security import OAuth2PasswordBearer
from app.services.security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def authenticate_user(user_from_db, password: str):
    if not user_from_db:
        return False
    if not verify_password(password, user_from_db.get("hashed_password", "")):
        return False
    return user_from_db
