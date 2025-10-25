from sqlalchemy import select, and_
from app.db.tables import bookings_table, equipment_table


class BookingRepository:
    def __init__(self, table=bookings_table):
        self.table = table

    async def create(self, session, booking_data: dict):
        """Создаёт новую бронь"""
        query = self.table.insert().values(**booking_data).returning(self.table)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one()

    async def list(self, session):
        """Возвращает все бронирования"""
        query = select(self.table)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]

    async def get_by_equipment(self, session, equipment_id: int):
        """Возвращает брони по ID оборудования"""
        query = select(self.table).where(self.table.c.equipment_id == equipment_id)
        result = await session.execute(query)
        return [dict(row._mapping) for row in result]

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

    async def get_by_landlord(self, session, landlord_id: int):
        """Возвращает все бронирования для оборудования, принадлежащего арендодателю."""
        stmt = (
            select(self.table)
            .join(equipment_table, self.table.c.equipment_id == equipment_table.c.id)
            .where(equipment_table.c.landlord_id == landlord_id)
        )
        result = await session.execute(stmt)
        return [dict(row._mapping) for row in result]