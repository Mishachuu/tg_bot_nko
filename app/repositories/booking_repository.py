from sqlalchemy import select, and_
from app.db.tables import bookings_table


class BookingRepository:
    def __init__(self, table=bookings_table):
        self.table = table

    async def post(self, session, booking_data: dict):
        """Создаёт новую бронь"""
        query = self.table.insert().values(**booking_data).returning(self.table)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()

    async def get_all(self, session):
        """Возвращает все бронирования"""
        query = select(self.table)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]
    
    async def get_by_user_id(self, session, user_id):
        query = select(self.table).where(self.table.c.user_id == user_id)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]


    async def get_by_equipment_id(self, session, equipment_id: int):
        """Возвращает брони по ID оборудования"""
        query = select(self.table).where(self.table.c.equipment_id == equipment_id)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]


    #===== Всё что ниже по идее нужно перенести в Service 
    async def find_conflicting(self, session, equipment_id: int, date_from, date_to):
        """
        Проверяет, есть ли пересечение бронирования по датам.
        Возвращает список конфликтующих броней.
        """
        query = select(self.table).where(
            and_(
                self.table.c.equipment_id == equipment_id,
                # Пересечение по диапазону дат
                self.table.c.date_from <= date_to,
                self.table.c.date_to >= date_from,
            )
        )
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]

    async def get_overlapping_bookings(self, session, equipment_id, date_from, date_to):
        query = (
            select(self.table)
            .where(
                self.table.c.equipment_id == equipment_id,
                self.table.c.date_from <= date_to,
                self.table.c.date_to >= date_from,
            )
        )
        result = await session.execute(query)
        return result.mappings().all()
