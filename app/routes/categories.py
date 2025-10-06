import logging
from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Response, status, Depends
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.models.data import Category as CategoryModel
from app.schemas.category import CategoryCreate, Category as CategorySchema
from app.dependencies.authentication import get_current_active_user
from app.schemas.user import User

router = APIRouter()


@router.get(
    "/",
    summary="Pegar todas as categorias",
    response_model=List[CategorySchema],
    response_description="Lista de todas as categorias cadastradas",
    status_code=HTTP_200_OK,
)
async def get_categories(
    _: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
    limit: int = 100,
) -> List[CategorySchema]:
    """Pegar todas as categorias cadastradas no banco de dados."""
    query = select(CategoryModel).limit(limit)
    result = await session.execute(query)
    categories = result.scalars().all()
    return [CategorySchema.from_orm(c) for c in categories]


@router.post(
    "/",
    summary="Criar uma nova categoria",
    response_description="Categoria criada com sucesso",
    status_code=HTTP_201_CREATED,
)
async def create_category(
    _: Annotated[User, Depends(get_current_active_user)],
    category: CategoryCreate,
    session: AsyncSession = Depends(get_session),
):
    """Criar uma nova categoria."""

    # Verificar se a categoria já existe
    query = select(CategoryModel).where(CategoryModel.name == category.name)
    result = await session.execute(query)
    category_exists = result.scalar_one_or_none()
    if category_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A categoria já existe.",
        )

    # Inserir a categoria no banco de dados
    new_category = CategoryModel(name=category.name)
    session.add(new_category)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await session.refresh(new_category)

    return CategorySchema.from_orm(new_category)