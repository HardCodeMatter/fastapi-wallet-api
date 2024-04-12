from fastapi import HTTPException, status
from sqlalchemy import select

from services import BaseService
from .models import User


class UserService(BaseService):
    async def create_user(self): ...

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
