from sqlalchemy import Table, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.tables import city_table

class CityRepository:
    def __init__(self, table=city_table):
        self.table = table

    async def add_city(self, session: AsyncSession, name: str):
        """Создаёт новый город"""
        # Проверяем существование города
        check_query = select(self.table).where(self.table.c.name == name)
        existing_city = await session.execute(check_query)
        if existing_city.first():
            return existing_city.scalar_one()
        
        # Создаем город
        query = self.table.insert().values(name=name)
        await session.execute(query)
        await session.commit()
        
        # Получаем созданный город
        get_query = select(self.table).where(self.table.c.name == name)
        result = await session.execute(get_query)
        return result.scalar_one()

    async def get_all(self, session: AsyncSession):
        """Возвращает все города"""
        query = select(self.table)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]
    
    async def get_by_id(self, session: AsyncSession, id: int):
        query = select(self.table).where(self.table.c.id == id)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]