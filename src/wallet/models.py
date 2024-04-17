import typing
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if typing.TYPE_CHECKING:
    from auth.models import User


class Account(Base):
    __tablename__ = 'accounts'

    uuid: Mapped[str] = mapped_column(primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(String(30), unique=True)
    
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.uuid', ondelete='CASCADE'))
    creator: Mapped['User'] = relationship(back_populates='accounts')

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())

    is_private: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f'Account(uuid={self.uuid}, name={self.name}, creator={self.creator}, is_private={self.is_private})'
    