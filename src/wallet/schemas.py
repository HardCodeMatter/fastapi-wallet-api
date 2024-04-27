import re
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from auth import schemas

from .models import RecordType


class AccountBase(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if ' ' in value.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Account name can not contain spaces',
            )

        if len(value.strip()) < 3 or len(value.strip()) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Account name must be between 3 and 30 characters in length, inclusive.',
            )

        return value.strip()


class AccountCreate(AccountBase):
    is_private: bool


class AccountRead(AccountBase):
    uuid: str
    is_private: bool
    creator: 'schemas.UserRead'


class AccountListRead(AccountBase):
    uuid: str
    is_private: bool


class AccountUpdate(AccountBase):
    is_private: bool


class CategoryBase(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value.strip()) < 3 or len(value.strip()) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Category name must be between 3 and 30 characters in length, inclusive.',
            )
        
        if not re.match(r'^[a-zA-Z\s]+$', value.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Category name must only contain letters.',
            )
        
        return value.strip().capitalize()


class CategoryCreate(CategoryBase): ...


class CategoryRead(CategoryBase):
    uuid: str
    creator: 'schemas.UserRead'


class CategoryUpdate(CategoryBase): ...


class RecordBase(BaseModel):
    type: 'RecordType'


class RecordCreate(RecordBase):
    amount: int


class RecordRead(RecordBase):
    uuid: str
