from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.booking import Booking
from datetime import datetime

class BookingRepository:
    def __init__(self):
        self.model = Booking

    async def create(self, session: AsyncSession, booking_data: dict) -> Booking:
        booking = Booking(**booking_data)
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking

    async def get_by_id(self, session: AsyncSession, booking_id: int) -> Booking | None:
        stmt = select(self.model).where(self.model.id == booking_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, session: AsyncSession, user_id: int):
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_equipment_id(self, session: AsyncSession, equipment_id: int):
        stmt = select(self.model).where(self.model.equipment_id == equipment_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_overlapping_bookings(self, session: AsyncSession, equipment_id: int, date_from: datetime, date_to: datetime):
        """Найти пересекающиеся бронирования"""
        stmt = select(self.model).where(
            and_(
                self.model.equipment_id == equipment_id,
                self.model.date_from <= date_to,
                self.model.date_to >= date_from
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def find_conflicting(self, session: AsyncSession, equipment_id: int, date_from: datetime, date_to: datetime):
        """Найти конфликтующие бронирования (алиас для get_overlapping_bookings)"""
        return await self.get_overlapping_bookings(session, equipment_id, date_from, date_to)
        