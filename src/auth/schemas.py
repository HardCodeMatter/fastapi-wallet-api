import re
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserBase(BaseModel):
    username: str
    email: str = Field(min_length=5, max_length=320)

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        if ' ' in value.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username cannot contain spaces.',
            )
        
        if len(value.strip()) < 3 or len(value.strip()) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username must be between 3 and 20 characters in length, inclusive.',
            )
        
        if not re.match(r'^[\w.]+$', value.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username must only contain letters, numbers, underscores, and points',
            )
        
        return value.lower()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        validation_expression = r'^[a-zA-Z0-9]+[.\w]*@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'

        if ' ' in value.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email cannot contain spaces.',
            )

        if not re.match(validation_expression, value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid email address',
            )
        
        return value.lower()


class UserCreate(UserBase):
    hashed_password: str


class UserRead(UserBase):
    uuid: str
