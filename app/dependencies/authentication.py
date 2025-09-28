
from fastapi import Depends, HTTPException, status
from typing import Annotated
from jose import JWTError
from app.database.db import database, users
from app.services.auth import oauth2_scheme
from app.services.jwt import SECRET_KEY, get_username_from_token
from app.schemas.token import TokenData
from app.schemas.user import User
from app.schemas.token import Token

async def get_current_user(token: Annotated[Token, Depends(oauth2_scheme)]):
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

    user = await database.fetch_one(
        users.select().where(users.c.username == token_data.username))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user