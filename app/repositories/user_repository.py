from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Update, Delete, Insert
from sqlalchemy import insert, select, update as sql_update, delete as sql_delete
from sqlalchemy.engine import Result
from typing import List, Optional


from app.models.user_app import AppUser

class UserRepository:
    def __init__(self):
        self.model = AppUser

    async def get_by_tgId(self, session: AsyncSession, tg_id: int) -> AppUser | None:
        stmt = select(self.model).where(self.model.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()  # Возвращает один объект или None

    async def get_by_id(self, session: AsyncSession, user_id: int) -> AppUser | None:
        stmt = select(self.model).where(self.model.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()  # Возвращает один объект или None
    
    async def add_user(self, session: AsyncSession, user: AppUser, is_lessor = False):
        user.is_lessor = is_lessor
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    async def get_all(self, session: AsyncSession):
        """Return:  List[AppUser]"""
        stmt = select(self.model)
        result = await session.execute(stmt)
        return result.scalars().all() 
    
    async def update(self, session: AsyncSession, user_id: int, changes: dict) -> AppUser | None:
        # Более эффективный способ - прямое обновление в БД
        stmt = (
            sql_update(self.model)
            .where(self.model.id == user_id)
            .values(**changes)
            .execution_options(synchronize_session="fetch")
        )
        
        result = await session.execute(stmt)
        await session.commit()
        
        if result.rowcount > 0:
            # Получаем обновленный объект
            return await self.get_by_id(session, user_id)
        return None
    
    async def delete_by_id(self, session: AsyncSession, user_id: int) -> dict | None:
        res = await session.execute(select(AppUser).where(self.table.c.id == user_id))
        user = res.scalars().one_or_none()
        if user is None:
            return False

        await session.delete(user)
        try:
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            raise

    async def get_users_paginated(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[AppUser]:
        """Получить пользователей с пагинацией"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_users_by_city(self, session: AsyncSession, city_id: int) -> List[AppUser]:
        """Получить пользователей по городу"""
        stmt = select(self.model).where(self.model.city_id == city_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_users_by_lessor_status(self, session: AsyncSession, is_lessor: bool) -> List[AppUser]:
        """Получить пользователей по статусу арендодателя"""
        stmt = select(self.model).where(self.model.is_lessor == is_lessor)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def search_users_by_name(self, session: AsyncSession, name_query: str) -> List[AppUser]:
        """Поиск пользователей по имени"""
        stmt = select(self.model).where(self.model.name.ilike(f"%{name_query}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_user_score(self, session: AsyncSession, user_id: int, score: float) -> AppUser | None:
        """Обновить рейтинг пользователя"""
        return await self.update(session, user_id, {"score": score})

    async def set_lessor_status(self, session: AsyncSession, user_id: int, is_lessor: bool) -> AppUser | None:
        """Установить статус арендодателя"""
        return await self.update(session, user_id, {"is_lessor": is_lessor})
