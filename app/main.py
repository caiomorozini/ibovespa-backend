from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import database
# from app.api.routes import api
from app.database.first_migration import create_first_user

async def startup():
    await database.connect()

async def shutdown():
    await database.disconnect()

async def app_lifespan(app: FastAPI):
    try:
        await startup()
        yield
    finally:
        await shutdown()


app = FastAPI(
    title="Ibovespa API",
    version="0.1",
    description="API para ",
    on_startup=[startup, create_first_user],
    on_shutdown=[shutdown],
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(api.router)