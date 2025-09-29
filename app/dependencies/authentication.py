from fastapi import Depends, HTTPException, status
from typing import Annotated
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db
from app.services.auth import oauth2_scheme
from app.services.jwt import SECRET_KEY, get_username_from_token
from app.schemas.token import TokenData
from app.models import User as UserModel  # ORM SQLAlchemy

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = get_username_from_token(token, SECRET_KEY)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as jwt_exc:
        raise credentials_exception from jwt_exc

    # Buscar usuário no banco com AsyncSession
    async with db.AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.username == token_data.username)
        )
        user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
