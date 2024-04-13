from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .services import UserService
from .utils import verify_password


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User:
    user = await UserService(session).get_user_by_username(username)

    if not user and not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Incorrect username or password.',
        )
    
    return user
