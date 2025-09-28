from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class NewUser(User):
    password: str
    role: str


class NewUserResponse(User):
    id: str


class UserResponse(User):
    id: str
    role_id: str


class Role(BaseModel):
    name: str
    description: str | None = None
