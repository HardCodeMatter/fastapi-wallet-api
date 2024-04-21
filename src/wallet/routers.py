from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from auth.models import User
from auth.utils import get_current_user, get_current_active_user

from .schemas import AccountCreate, AccountRead, AccountUpdate
from . import services


router = APIRouter(
    tags=['Wallet'],
)


@router.post('/accounts/create', status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AccountRead:
    return await services.AccountService(session).create_account(account_data, current_user)


@router.get('/accounts/{name}/')
async def get_account_by_name(
    name: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> AccountRead:
    account = await services.AccountService(session).get_account_by_name(name)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Account with this name is not found.',
        )
    
    if account.is_private and account.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot read this account, because it is a private.',
        )
    
    return account


@router.patch('/accounts/{uuid}/update')
async def update_account(
    uuid: str,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AccountRead:
    account = await services.AccountService(session).get_account_by_uuid(uuid)

    if account.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot update this account, because you are not creator.',
        )
    
    return await services.AccountService(session).update_account(uuid, account_data)
