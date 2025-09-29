from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Role, User
from app.database import db
from app.resources.config import settings
from app.services.security import get_password_hash


async def create_first_user():
    """
    Se variável "environment" for "development",
    cria role "admin" e usuário "admin"
    """
    async with db.AsyncSessionLocal() as session:  # cria sessão async
        # Checando se role admin existe
        result = await session.execute(
            select(Role).where(Role.name == "admin")
        )
        role = result.scalar_one_or_none()

        if not role:

            role = Role(
                name="admin",
                descr="Administrador do sistema"
            )
            session.add(role)
            await session.commit()  # commit para gerar o ID
            await session.refresh(role)  # pega o ID gerado

        # Checando se usuário admin existe
        result = await session.execute(
            select(User).where(User.username == settings.first_login)
        )
        user = result.scalar_one_or_none()
        if user:
            return

        # Criando usuário admin
        user = User(
            username=settings.first_login,
            hashed_password=get_password_hash(settings.first_password),
            email=settings.first_email,
            role_id=role.id,
            disabled=False
        )
        session.add(user)
        await session.commit()
