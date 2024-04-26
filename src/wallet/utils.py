from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User

from .models import Category


async def verify_unique_category_name(session: AsyncSession, category_name: str, current_user: User) -> bool:
    stmt = select(Category).filter(
        Category.creator_id == current_user.uuid,
        Category.name == category_name
    )

    category = (
        await session.execute(stmt)
    ).scalar()

    return category is not None
