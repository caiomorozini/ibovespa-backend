from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey, text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    id = Column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, unique=True, nullable=False)
    descr = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=text("now()"),
        server_default=text("now()"),
    )

    # relação ORM
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(String, primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String, unique=True, nullable=False)
    role_id = Column(String, ForeignKey("auth.roles.id"), nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=text("now()"),
        server_default=text("now()"),
    )

    # relação ORM
    role = relationship("Role", back_populates="users")
