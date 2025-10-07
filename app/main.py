from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.first_migration import create_first_user
from app.database import db
from app.models import User
from app.services.auth import authenticate_user
from app.dependencies.authentication import get_current_active_user
from app.routes.auth import router as auth_router

app = FastAPI(
    title="Celular",
    version="0.1",
    description="API para dados de celulares",
    on_startup=[db.startup, create_first_user],
    on_shutdown=[db.shutdown],
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(
    prefix="/api/v1/data",
    router=__import__("app.routes.data", fromlist=["router"]).router,
)
app.include_router(
    prefix="/api/v1/categories",
    router=__import__("app.routes.categories", fromlist=["router"]).router,
)

app.include_router(
    prefix="/api/v1/modelo",
    router=__import__("app.routes.modelo", fromlist=["router"]).router,
)
@app.get("/users")
async def list_users(session: AsyncSession = Depends(db.get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


# Teste de autenticação
@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
