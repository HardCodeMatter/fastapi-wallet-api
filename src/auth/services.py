from fastapi import HTTPException, status
from sqlalchemy import select

from services import BaseService

from .models import User
from .schemas import UserCreate
from .utils import hash_password


class UserService(BaseService):
    async def create_user(self, user_data: UserCreate) -> User:
        username = await UserService(self.session).get_user_by_username(user_data.username)

        if username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with this username is already exist.',
            )
        
        email = await UserService(self.session).get_user_by_email(user_data.email)

        if email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with this email is already exist.',
            )
        
        user_data.hashed_password = hash_password(user_data.hashed_password)

        user = User(**user_data.model_dump())

        self.session.add(user)
        await self.session.commit()

        return user

    async def get_user_by_uuid(self, uuid: str) -> User:
        user = await self.session.execute(
            select(User).filter(User.uuid == uuid)
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User with this UUID is not found.',
            )
        
        await self.session.commit()

        return user.scalar()

    async def get_user_by_username(self, username: str) -> User:
        user = await self.session.execute(
            select(User).filter(User.username == username)
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User with this username is not found.',
            )
        
        await self.session.commit()

        return user.scalar()

    async def get_user_by_email(self, email: str):
        user = await self.session.execute(
            select(User).filter(User.email == email)
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User with this email is not found.',
            )
        
        await self.session.commit()

        return user.scalar()
