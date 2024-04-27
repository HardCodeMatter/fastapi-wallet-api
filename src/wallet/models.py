import typing
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if typing.TYPE_CHECKING:
    from auth.models import User


class Account(Base):
    __tablename__ = 'accounts'

    uuid: Mapped[str] = mapped_column(primary_key=True, default=str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(30), unique=True)
    
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.uuid', ondelete='CASCADE'))
    creator: Mapped['User'] = relationship(back_populates='accounts')

    records: Mapped[list['Record']] = relationship(back_populates='account')

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())

    is_private: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f'Account(uuid={self.uuid}, name={self.name}, creator={self.creator}, is_private={self.is_private})'
    

class Category(Base):
    __tablename__ = 'categories'

    uuid: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(30))

    creator_id: Mapped[int] = mapped_column(ForeignKey('users.uuid'))
    creator: Mapped['User'] = relationship(back_populates='categories')

    records: Mapped[list['Record']] = relationship(back_populates='category')

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f'Category(uuid={self.uuid}, name={self.name}, creator={self.creator})'


class RecordType(enum.Enum):
    income = 'income'
    expense = 'expense'


class Record(Base):
    __tablename__ = 'records'

    uuid: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    type: Mapped[RecordType]
    amount: Mapped[int]

    creator_id: Mapped[int] = mapped_column(ForeignKey('users.uuid'))
    creator: Mapped['User'] = relationship(back_populates='records')
    
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.uuid'))
    account: Mapped['Account'] = relationship(back_populates='records')

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.uuid'))
    category: Mapped['Category'] = relationship(back_populates='records')

    def __repr__(self) -> str:
        return f'Record(uuid={self.uuid}, amount={self.amount}, creator={self.creator}, account={self.account}, category={self.category})'
