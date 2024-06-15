from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload

from services import BaseService
from auth.models import User

from .models import Account, Category, Record, RecordType
from .schemas import (
    AccountCreate, AccountUpdate, AccountRead,
    CategoryCreate, CategoryUpdate, CategoryRead,
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
                select(
                    Account.uuid, Account.name, Account.is_private, Account.creator_id.label('creator_id'),
                    User.uuid.label('user_uuid'), User.username, User.email,
                    func.coalesce(func.sum(Record.amount), 0).label('amount')
                )
                .filter(Account.name == name)
                .join(Record, Record.account_id == Account.uuid, isouter=True)
                .join(User, User.uuid == Account.creator_id, isouter=True)
                .group_by(Account.uuid, User.uuid)
            )
        ).mappings().one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Account with this name is not found.',
            )

        account_data = {
            'uuid': account['uuid'],
            'name': account['name'],
            'creator_id': account['creator_id'],
            'is_private': account['is_private'],
            'creator': {
                'uuid': account['user_uuid'],
                'username': account['username'],
                'email': account['email'],
            },
            'amount': account['amount']
        }

        await self.session.commit()

        return AccountRead(**account_data)
    
    async def get_accounts_by_creator_id(self, uuid: str) -> list[Account]:
        accounts = (
            await self.session.execute(
                select(
                    Account.uuid,
                    Account.name,
                    Account.creator_id,
                    Account.is_private,
                    func.coalesce(func.sum(Record.amount), 0).label('amount')
                )
                .filter(Account.creator_id == uuid)
                .join(Record, Record.account_id == Account.uuid, isouter=True)
                .group_by(Account.uuid)
            )
        ).mappings().all()

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
                select(
                    Category.uuid, Category.name,
                    User.uuid.label('user_uuid'), User.username, User.email,
                    func.coalesce(func.sum(Record.amount), 0).label('amount')
                )
                .filter(Category.uuid == uuid)
                .join(Record, Record.category_id == Category.uuid, isouter=True)
                .join(User, User.uuid == Category.creator_id, isouter=True)
                .group_by(Category.uuid, User.uuid)
            )
        ).mappings().one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category is not found.',
            )

        category_data = {
            'uuid': category['uuid'],
            'name': category['name'],
            'creator': {
                'uuid': category['user_uuid'],
                'username': category['username'],
                'email': category['email'],
            },
            'amount': category['amount']
        }

        await self.session.commit()

        return CategoryRead(**category_data)
    
    async def get_categories_by_creator_id(self, user_uuid: str) -> list[Category]:
        categories = (
            await self.session.execute(
                select(
                    Category.uuid,
                    Category.name,
                    Category.creator_id,
                    func.coalesce(func.sum(Record.amount), 0).label('amount')
                )
                .filter(Category.creator_id == user_uuid)
                .join(Record, Record.category_id == Category.uuid, isouter=True)
                .group_by(Category.uuid, Record.category_id)
            )
        ).mappings().all()
        
        await self.session.commit()

        return categories
    
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

        amount: RecordType = record_data.amount if record_data.type == RecordType.income else -(record_data.amount)
        
        record_dict = record_data.model_dump()
        record_dict['amount'] = amount

        record = Record(
            creator_id=current_user.uuid,
            **record_dict,
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
