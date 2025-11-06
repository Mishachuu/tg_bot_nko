from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

class CategoryRepository:
    def __init__(self, table):
        self._t = table

    async def add_category(self, session, category: dict):
        # ожидаем дикт вроде {"id": 1, "name": "...", "is_accepted": True}
        stmt = insert(self._t).values(**category).returning(self._t)
        res = await session.execute(stmt)
        return res.fetchone()


    async def get_all(self, session: AsyncSession):
        stmt = select(self._t).order_by(self._t.c.id)
        res = await session.execute(stmt)
        return [dict(r._mapping) for r in res.fetchall()]
