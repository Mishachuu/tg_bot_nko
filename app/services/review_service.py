from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.review_repository import ReviewRepository

class ReviewService:
    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    async def add_review(self, session: AsyncSession, *, equipment_id: int, renter_id: int, owner_id: int, rating: int, comment: str | None):
        rating = max(1, min(5, int(rating)))
        data = {
            "equipment_id": equipment_id,
            "renter_id": renter_id,
            "owner_id": owner_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(tz=timezone.utc).replace(tzinfo=None),
        }
        new_id = await self.repo.add(session, data)
        await session.commit()
        return new_id

    async def list_for_user(self, session: AsyncSession, renter_id: int):
        return await self.repo.list_by_user(session, renter_id)
