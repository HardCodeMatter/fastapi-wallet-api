from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session

from .managers import authenticate_user, create_access_token
from .models import User
from .schemas import Token, UserCreate, UserRead
from .utils import get_current_user
from . import services


router = APIRouter(
    tags=['Users'],
)


@router.post('/login', status_code=status.HTTP_200_OK)
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


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    return await services.UserService(session).create_user(user_data)


@router.get('/users/{username}/', dependencies=[Depends(get_current_user)])
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    user = await services.UserService(session).get_user_by_username(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with this username is not found.',
        )
    
    return user


@router.get('/users/profile')
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    return await services.UserService(session).get_user_by_username(current_user.username)
