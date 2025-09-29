from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.services.auth import authenticate_user
from app.services.jwt import create_access_token
from app.schemas.token import Token
from app.database import db

router = APIRouter()

@router.post("/api/v1/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db.get_session),
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not authenticate_user({"hashed_password": user.hashed_password}, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
