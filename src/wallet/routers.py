from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from auth.models import User
from auth.utils import get_current_user, get_current_active_user

from .schemas import (
    AccountCreate, AccountRead, AccountListRead, AccountUpdate,
    CategoryCreate, CategoryRead, CategoryUpdate,
    RecordCreate, RecordRead,
)
from . import services


router = APIRouter()


@router.post('/accounts', tags=['Accounts'], status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AccountRead:
    return await services.AccountService(session).create_account(account_data, current_user)


@router.get('/accounts/own', tags=['Accounts'], summary='Get owned accounts')
async def get_accounts_by_creator(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[AccountListRead]:
    accounts = await services.AccountService(session).get_accounts_by_creator_id(current_user.uuid)

    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Accounts are not found.',
        )

    return accounts


@router.get('/accounts', tags=['Accounts'])
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


@router.patch('/accounts/{uuid}', tags=['Accounts'])
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


@router.delete('/accounts/{uuid}', tags=['Accounts'])
async def delete_account(
    uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    account = await services.AccountService(session).get_account_by_uuid(uuid)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Account is not found.',
        )

    if account.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot delete this account, because you are not creator.',
        )
    
    return await services.AccountService(session).delete_account(uuid)


@router.post('/categories', tags=['Categories'], status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> CategoryRead:
    return await services.CategoryService(session).create_category(category_data, current_user)


@router.get('/categories/{uuid}', tags=['Categories'])
async def get_category_by_uuid(
    uuid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> CategoryRead:
    category = await services.CategoryService(session).get_category_by_uuid(uuid)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category is not found.',
        )
    
    if category.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot read this category, because you are not the creator.',
        )
    
    return category


@router.patch('/categories/{uuid}', tags=['Categories'])
async def update_category(
    uuid: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> CategoryRead:
    category = await services.CategoryService(session).get_category_by_uuid(uuid)

    if category.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot update this account, because you are not creator.',
        )
    
    return await services.CategoryService(session).update_category(uuid, category_data)


@router.delete('/categories/{uuid}', tags=['Categories'])
async def delete_category(
    uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    category = await services.CategoryService(session).get_category_by_uuid(uuid)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category is not found.',
        )

    if category.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cannot delete this category, because you are not creator.',
        )
    
    return await services.CategoryService(session).delete_category(uuid)


@router.post('/records', tags=['Records'], status_code=status.HTTP_201_CREATED)
async def create_record(
    record_data: RecordCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> RecordRead:
    return await services.RecordService(session).create_record(record_data, current_user)


@router.get('/records/{uuid}', tags=['Records'])
async def get_record_by_uuid(
    uuid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> RecordRead:
    record = await services.RecordService(session).get_record_by_uuid(uuid)

    if not record or record.creator_id != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Record is not found.',
        )
    
    return record


@router.delete('/records/{uuid}', tags=['Records'])
async def delete_record(
    uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await services.RecordService(session).delete_record(uuid, current_user)
