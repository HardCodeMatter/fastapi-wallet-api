from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from services import BaseService
from auth.models import User

from .models import Account, Category
from .schemas import AccountCreate, AccountUpdate, CategoryCreate


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
