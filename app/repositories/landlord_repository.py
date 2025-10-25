from sqlalchemy import select, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from models.user import User
from models.owner import Owner
from db import AsyncSessionLocal


class LandlordRepository:
    """
    Репозиторий для работы с арендодателями (Owner).
    Предоставляет асинхронные CRUD операции.
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session or AsyncSessionLocal()

    async def create(self, owner: Owner) -> Owner:
        """
        Создание нового арендодателя в БД.
        """
        async with self._session as session:
            async with session.begin():
                session.add(owner)
                await session.flush()
                await session.refresh(owner)
                return owner

    async def get_by_id(self, owner_id: int) -> Optional[Owner]:
        """
        Получение арендодателя по ID.
        """
        async with self._session as session:
            result = await session.execute(
                select(Owner).where(Owner.id == owner_id)
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[Owner]:
        """
        Получение всех арендодателей.
        """
        async with self._session as session:
            result = await session.execute(select(Owner))
            return result.scalars().all()

    async def update(self, owner_id: int, data: dict) -> Optional[Owner]:
        """
        Обновление данных арендодателя.
        """
        async with self._session as session:
            async with session.begin():
                await session.execute(
                    sql_update(Owner)
                    .where(Owner.id == owner_id)
                    .values(**data)
                )
                result = await session.execute(
                    select(Owner).where(Owner.id == owner_id)
                )
                return result.scalar_one_or_none()

    async def delete(self, owner_id: int) -> bool:
        """
        Удаление арендодателя по ID.
        Возвращает True, если запись была удалена.
        """
        async with self._session as session:
            async with session.begin():
                result = await session.execute(
                    sql_delete(Owner).where(Owner.id == owner_id)
                )
                return result.rowcount > 0
