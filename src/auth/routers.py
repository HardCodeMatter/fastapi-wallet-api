from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session

from .managers import authenticate_user, create_access_token
from .schemas import Token


router = APIRouter(
    tags=['Users'],
)


@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await authenticate_user(
        session=session,
        username=form_data.username,
        password=form_data.password,
    )

    access_token = create_access_token(subject=user.username)

    return Token(
        access_token=access_token,
        token_type='bearer',
    )
