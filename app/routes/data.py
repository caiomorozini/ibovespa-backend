import logging
import json
import sqlalchemy
import pandas as pd
from fastapi import (APIRouter, HTTPException, Response, status, File, UploadFile, Depends)
from starlette import status
from app.models import Registration, Category
from app.database.db import get_session, AsyncSession
from app.schemas.register import Register
from app.schemas.category import Category as CategorySchema
from typing import List, Annotated
from app.dependencies.authentication import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get(
    _: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
    limit: int = 3
):
    query = sqlalchemy.select(Registration).limit(limit)
    x = await session.execute(query)
    return x.scalars().all()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create(
    # _: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
    register: Register = None
):

    logging.info("Dados recebidos, verificando se já existe na base de dados...")

    # Busca o item na base de dados pelo nome
    item = await session.execute(
        sqlalchemy.select(Registration).where(
                Registration.name == register.name
            )
    )
    item = item.scalar_one_or_none()

    if item:
        logging.info("Registro já existe na base de dados")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registro já existe na base de dados"
        )

    # Checando se categoria existe
    category = await session.execute(
        sqlalchemy.select(Category).where(
                Category.name == register.category
            )
    )
    category = category.scalar_one_or_none()
    if not category:
        # Criando categoria
        logging.info("Categoria não existe na base de dados, inserindo...")
        _ = await session.execute(
            sqlalchemy.insert(Category).values(
                name=register.category,
        ))
        await session.commit()
        logging.info("Categoria inserida com sucesso")
        category = await session.execute(
            sqlalchemy.select(Category).where(
                    Category.name == register.category
                )
        )
        category = category.scalar_one_or_none()

    logging.info("Registro não existe na base de dados, inserindo...")

    _ = await session.execute(
        sqlalchemy.insert(Registration).values(
            **register.model_dump()
    ))
    await session.commit()
    logging.info("Registro inserido com sucesso")
    return Response(status_code=status.HTTP_201_CREATED)
