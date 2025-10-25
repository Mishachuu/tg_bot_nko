from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result


class EquipmentPhotoRepository:
    def __init__(self, table):
        self._t = table

    async def add_photo(self, session: AsyncSession, equipment_id: int, filename: str, content: bytes) -> int:
        """Добавить фото, вернуть ID созданной записи."""
        stmt = (
            insert(self._t)
            .values(equipment_id=equipment_id, filename=filename, content=content)
            .returning(self._t.c.id)
        )
        res: Result = await session.execute(stmt)
        new_id = res.scalar_one()
        return new_id

    async def get_photos_by_equipment(self, session: AsyncSession, equipment_id: int) -> list[dict]:
        """Вернуть список фото для оборудования."""
        stmt = select(self._t).where(self._t.c.equipment_id == equipment_id)
        res: Result = await session.execute(stmt)
        return [dict(row._mapping) for row in res.fetchall()]

    async def delete_photo(self, session: AsyncSession, photo_id: int) -> bool:
        stmt = delete(self._t).where(self._t.c.id == photo_id)
        res = await session.execute(stmt)
        return (res.rowcount or 0) > 0
