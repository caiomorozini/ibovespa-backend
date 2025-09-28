from sqlalchemy.sql.expression import text
import databases
import sqlalchemy

from app.resources.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://" \
    f"{settings.database_username}:" \
    f"{settings.database_password}@" \
    f"{settings.database_hostname}:" \
    f"{settings.database_port}/" \
    f"{settings.database_name}"

database = databases.Database(SQLALCHEMY_DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)

# Checando se schema existe
engine.execute(
    text(
        "CREATE SCHEMA IF NOT EXISTS auth"
    )
)

engine.execute(
    text(
        "CREATE SCHEMA IF NOT EXISTS shipping"
    )
)

engine.execute(
    text(
        "CREATE SCHEMA IF NOT EXISTS public"
    )
)

roles = sqlalchemy.Table(
    "roles",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.String,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    ),
    sqlalchemy.Column(
        "name",
        sqlalchemy.String,
        unique=True,
        nullable=False
    ),
    sqlalchemy.Column(
        "descr",
        sqlalchemy.String,
        nullable=True
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        server_default=text("now()"),
    ),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        onupdate=text("now()"),
        server_default=text("now()"),
    ),
    schema="auth",
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.String,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    ),
    sqlalchemy.Column(
        "username",
        sqlalchemy.String,
        unique=True,
        nullable=False
    ),
    sqlalchemy.Column(
        "role_id",
        sqlalchemy.String,
        sqlalchemy.ForeignKey("auth.roles.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "hashed_password",
        sqlalchemy.String,
        nullable=False
    ),
    sqlalchemy.Column(
        "disabled",
        sqlalchemy.Boolean,
    ),
    sqlalchemy.Column(
        "email",
        sqlalchemy.String,
        unique=True,
        nullable=False,
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        server_default=text("now()"),
    ),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        onupdate=text("now()"),
        server_default=text("now()"),
    ),
    schema="auth",
)

metadata.create_all(engine)
