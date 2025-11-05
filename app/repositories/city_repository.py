from sqlalchemy import select, and_
from app.db.tables import city_table


class CityRepository:
    def __init__(self, table=city_table):
        self.table = table

    async def add_city(self, session, name):
        """Создаёт новую бронь"""
        query = self.table.insert().values(name=name)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()

    async def get_all(self, session):
        """Возвращает все бронирования"""
        query = select(self.table)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]
    
    async def get_by_id(self, session, id):
        query = select(self.table).where(self.table.c.id == id)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]