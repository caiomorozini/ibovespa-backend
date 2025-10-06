from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
