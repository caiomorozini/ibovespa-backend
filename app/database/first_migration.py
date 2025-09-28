
from app.database.db import database
from app.resources.config import settings
from app.database import db
from app.services.security import get_password_hash

async def create_first_user():
    """
    Se variável "environment" for "development",
    cria role "admin" e usuário "admin"
    """

    # Checando se role admin existe
    query = db.roles.select().where(db.roles.c.name == "admin")
    role = await database.fetch_one(query)
    if not role:
        # Criando role admin
        query = db.roles.insert().values(
            name="admin",
            descr="Administrador do sistema"
        )
        await database.execute(query)

    # Checando se usuário admin existe
    query = db.users.select().where(db.users.c.username == "admin")
    user = await database.fetch_one(query)
    if user:
        return

    query_role = db.roles.select().where(
        db.roles.c.name == "admin"
    )

    role_from_db = await database.fetch_one(
        query_role
    )

    # Criando usuário admin
    query = db.users.insert().values(
        username=settings.first_login,
        hashed_password=get_password_hash(
            settings.first_password),
        email=settings.first_email,
        role_id=role_from_db["id"],
        disabled=False
    )

    await database.execute(query)