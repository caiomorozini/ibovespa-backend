from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String, TIMESTAMP, Integer, Float, JSON, ForeignKey, text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


# Registrations
# Categories
class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "data"}

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    registrations: Mapped[List["Registration"]] = relationship(back_populates="category_rel", cascade="all, delete-orphan")


# Registrations
class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = {"schema": "data"}

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String, unique=True)
    category: Mapped[str] = mapped_column(ForeignKey("data.categories.name"))
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[Optional[int]] = mapped_column(Integer)
    data: Mapped[Optional[dict]] = mapped_column(JSON)
    url: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    category_rel: Mapped["Category"] = relationship(back_populates="registrations")
    prices: Mapped[List["Price"]] = relationship(back_populates="registration_rel", cascade="all, delete-orphan")


# Prices
class Price(Base):
    __tablename__ = "prices"
    __table_args__ = {"schema": "data"}

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    registration_id: Mapped[str] = mapped_column(ForeignKey("data.registrations.id"))
    price: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    registration_rel: Mapped["Registration"] = relationship(back_populates="prices")
