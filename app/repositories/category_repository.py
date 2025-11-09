from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category

class CategoryRepository:
    def __init__(self):
        self.model = Category

    async def get_by_id(self, session: AsyncSession, category_id: int) -> Category | None:
        stmt = select(self.model).where(self.model.id == category_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession):
        stmt = select(self.model)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, category_data: dict) -> Category:
        category = Category(**category_data)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category