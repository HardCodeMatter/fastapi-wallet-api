from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    hashed_password: str


class UserRead(UserBase):
    uuid: str
