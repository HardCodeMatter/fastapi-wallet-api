from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from services import BaseService
from auth.models import User

from .models import Account, Category, Record
from .schemas import (
    AccountCreate, AccountUpdate,
    CategoryCreate, CategoryUpdate,
    RecordCreate,
)
from .utils import verify_unique_category_name


class AccountService(BaseService):
    async def create_account(self, account_data: AccountCreate, current_user: User) -> Account:
        account = await self.get_account_by_name(account_data.name)

        if account:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Account with this name is already exist.',
            )

        account = Account(
            creator_id=current_user.uuid,
            **account_data.model_dump(),
        )

        self.session.add(account)
        await self.session.commit()

        return account
    
    async def get_account_by_uuid(self, uuid: str) -> Account:
        account = (
            await self.session.execute(
                select(Account)
                .filter(Account.uuid == uuid)
                .options(joinedload(Account.creator))
            )
        ).scalar()

        await self.session.commit()

        return account

    async def get_account_by_name(self, name: str) -> Account:
        account = (
            await self.session.execute(
                select(Account)
                .filter(Account.name == name)
                .options(joinedload(Account.creator))
            )
        ).scalar()

        await self.session.commit()

        return account
    
    async def get_accounts_by_creator_id(self, uuid: str) -> list[Account]:
        accounts = (
            await self.session.execute(
                select(Account)
                .filter(Account.creator_id == uuid)
            )
        ).scalars().all()

        await self.session.commit()

        return accounts
    
    async def get_account_with_records(self, uuid: str, current_user: User) -> Account:
        account = (
            await self.session.execute(
                select(Account)
                .filter(Account.uuid == uuid, Account.creator_id == current_user.uuid, Record.account_id == uuid)
                .options(selectinload(Account.records))
            )
        ).scalar()

        if not account or (account.is_private and account.creator_id != current_user.uuid):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Account is not found.',
            )

        await self.session.commit()

        return account

    async def update_account(self, uuid: int, account_data: AccountUpdate) -> Account:
        account = await self.get_account_by_uuid(uuid)

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Account is not found.',
            )
        
        account.name = account_data.name
        account.is_private = account_data.is_private

        await self.session.commit()

        return account
    
    async def delete_account(self, uuid: str) -> Account:
        account = await self.get_account_by_uuid(uuid)
        
        await self.session.delete(account)
        await self.session.commit()

        return {
            'detail': 'Account is deleted successful.',
        }


class CategoryService(BaseService):
    async def create_category(self, category_data: CategoryCreate, current_user: User) -> Category:
        if await verify_unique_category_name(session=self.session, category_name=category_data.name, current_user=current_user):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Category with this name is already exist.',
            )
        
        category = Category(
            creator_id=current_user.uuid,
            **category_data.model_dump(),
        )

        self.session.add(category)
        await self.session.commit()

        return category

    async def get_category_by_uuid(self, uuid: str) -> Category:
        category = (
            await self.session.execute(
                select(Category)
                .filter(Category.uuid == uuid)
                .options(joinedload(Category.creator))
            )
        ).scalar()

        await self.session.commit()

        return category
    
    async def get_category_with_records(self, uuid: str, current_user: User) -> Category:
        stmt = (
            select(Category)
            .filter(Category.uuid == uuid, Category.creator_id == current_user.uuid, Record.category_id == uuid)
            .options(selectinload(Category.records))
        )
        
        category: Category = (
            await self.session.execute(stmt)
        ).scalar()

        if not category or category.creator_id != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category is not found.',
            )
        
        await self.session.commit()

        return category
    
    async def update_category(self, uuid: str, category_data: CategoryUpdate) -> Category:
        category = await self.get_category_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category is not found.',
            )
        
        category.name = category_data.name

        await self.session.commit()

        return category

    async def delete_category(self, uuid: str) -> dict:
        category = await self.get_category_by_uuid(uuid)

        await self.session.delete(category)
        await self.session.commit()

        return {
            'detail': 'Category is deleted successful.',
        }


class RecordService(BaseService):
    async def create_record(self, record_data: RecordCreate, current_user: User) -> Record:
        account = await AccountService(self.session).get_account_by_uuid(record_data.account_id)

        if not account or account.creator_id != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Account is not found.',
            )
        
        category = await CategoryService(self.session).get_category_by_uuid(record_data.category_id)

        if not category or category.creator_id != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category is not found.',
            )
        
        record = Record(
            creator_id=current_user.uuid,
            **record_data.model_dump(),
        )

        self.session.add(record)
        await self.session.commit()

        return record

    async def get_record_by_uuid(self, uuid: str) -> Record:
        stmt = select(Record).filter(Record.uuid == uuid)

        record = (
            await self.session.execute(stmt)
        ).scalar()

        await self.session.commit()

        return record

    async def delete_record(self, uuid: str, current_user: User) -> dict:
        record = await self.get_record_by_uuid(uuid)

        if not record or record.creator_id != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Record is not found.',
            )
        
        await self.session.delete(record)
        await self.session.commit()
        
        return {
            'detail': 'Record is deleted successful.'
        }
