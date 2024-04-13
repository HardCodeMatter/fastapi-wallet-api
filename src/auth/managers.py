from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from .config import auth_settings
from .models import User
from .services import UserService
from .utils import verify_password


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User:
    user = await UserService(session).get_user_by_username(username)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Incorrect username or password.',
        )
    
    return user


def create_access_token(subject: str, expires_delta: int | None = None):
    if not expires_delta:
        expires_delta = datetime.now(UTC) + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_delta = datetime.now(UTC) + expires_delta
    
    to_encode = {'sub': subject, 'exp': expires_delta}
    encoded_jwt = jwt.encode(
        to_encode,
        key=auth_settings.SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
    )

    return encoded_jwt
