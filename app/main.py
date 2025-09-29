from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.first_migration import create_first_user
from app.database import db
from app.models import User

app = FastAPI(
    title="Ibovespa API",
    version="0.1",
    description="API para ",
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

# Exemplo: buscar usuários
@app.get("/users")
async def list_users(session: AsyncSession = Depends(db.get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users
