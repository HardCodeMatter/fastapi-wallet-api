from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from services import BaseService
from auth.models import User

from .models import Account
from .schemas import AccountCreate


class WalletService(BaseService):
    async def create_account(self, account_data: AccountCreate, current_user: User) -> Account:
        account = await self.get_account_by_name(account_data.name)

        if account:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Account with this username is already exist.',
            )

        account = Account(
            creator_id=current_user.uuid,
            **account_data.model_dump(),
        )

        self.session.add(account)
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
