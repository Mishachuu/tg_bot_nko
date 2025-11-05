from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Update, Delete, Insert
from sqlalchemy import insert, select, update as sql_update, delete as sql_delete
from sqlalchemy.engine import Result


from app.models.user_app import AppUser

class UserRepository:
    def __init__(self):
        self.model = AppUser

    # ====== CRUD =====

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
    
    async def add_user(self, session: AsyncSession, user: AppUser, publish = False):
        user.publish = publish
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
        # 1) Получаем объект
        res = await session.execute(select(AppUser).where(self.table.c.id == user_id))
        user = res.scalars().one_or_none()
        if user is None:
            return None

        # 2) Применяем изменения (changes — dict с полями, которые нужно обновить)
        for k, v in changes.items():
            if hasattr(user, k):
                setattr(user, k, v)

        # 3) Сохраняем измененя
        await session.commit()
        await session.refresh(user)  # подтянуть актуальные поля
        return user
    
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