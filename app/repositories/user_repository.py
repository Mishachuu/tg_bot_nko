from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Update, Delete, Insert
from sqlalchemy import insert, select, update as sql_update, delete as sql_delete
from sqlalchemy.engine import Result

from app.db.tables import user_table
from app.models.user_app import AppUser

class UserRepository:
    def __init__(self, table=user_table):
        self.table = table

    # ====== CRUD =====
    async def get_by_tgId(self, session: AsyncSession, tg_id: int) -> AppUser | None:
        stmt = select(AppUser).where(AppUser.tg_id == tg_id)
        res = await session.execute(stmt)
        user = res.scalars().one_or_none()   # <- scalars() возвращает ORM-объекты
        return user

    async def get_by_id(self, session: AsyncSession, id : int ):
        stmt : Select = select(AppUser).where(self.table.c.id == id)
        res : Result = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user is None:
            return None
        return user
    
    async def post(self, session: AsyncSession, user: AppUser):
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    async def update_by_id(self, session: AsyncSession, user_id: int, changes: dict) -> AppUser | None:
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


