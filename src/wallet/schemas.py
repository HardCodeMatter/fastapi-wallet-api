from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from auth import schemas


class AccountBase(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value.strip()) < 3 or len(value.strip()) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username must be between 3 and 30 characters in length, inclusive.',
            )

        return value.strip()


class AccountCreate(AccountBase):
    creator_id: int
    is_private: bool


class AccountRead(AccountBase):
    uuid: str
    creator: 'schemas.UserRead'
