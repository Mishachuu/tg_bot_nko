from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.review import Review

class ReviewRepository:
    def __init__(self):
        self.model = Review

    async def create(self, session: AsyncSession, review_data: dict) -> Review:
        review = Review(**review_data)
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review

    async def get_by_id(self, session: AsyncSession, review_id: int) -> Review | None:
        stmt = select(self.model).where(self.model.id == review_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_equipment_id(self, session: AsyncSession, equipment_id: int):
        stmt = select(self.model).where(self.model.equipment_id == equipment_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_renter_id(self, session: AsyncSession, renter_id: int):
        stmt = select(self.model).where(self.model.renter_id == renter_id)
        result = await session.execute(stmt)
        return result.scalars().all()