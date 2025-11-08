from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from app.db.tables import reviews_table

class ReviewRepository:
    def __init__(self, table=reviews_table):
        self.t = table

    async def add(self, session: AsyncSession, data: dict) -> int:
        stmt = insert(self.t).values(**data).returning(self.t.c.id)
        res: Result = await session.execute(stmt)
        return res.scalar_one()

    async def list_by_equipment(self, session: AsyncSession, equipment_id: int) -> list[dict]:
        res = await session.execute(select(self.t).where(self.t.c.equipment_id == equipment_id))
        return [dict(r._mapping) for r in res.fetchall()]

    async def list_by_user(self, session: AsyncSession, renter_id: int) -> list[dict]:
        res = await session.execute(select(self.t).where(self.t.c.renter_id == renter_id))
        return [dict(r._mapping) for r in res.fetchall()]
