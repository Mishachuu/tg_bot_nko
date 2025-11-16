from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.equipment import Equipment


class BookingRepository:
    def __init__(self):
        self.model = Booking

    # ----------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------
    async def create(self, session: AsyncSession, booking_data: dict) -> Booking:
        booking = Booking(**booking_data)
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking

    # ----------------------------------------------------------------------
    # GET
    # ----------------------------------------------------------------------
    async def get_by_id(self, session: AsyncSession, booking_id: int) -> Optional[Booking]:
        stmt = select(self.model).where(self.model.id == booking_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, session: AsyncSession, user_id: int) -> List[Booking]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_equipment_id(self, session: AsyncSession, equipment_id: int) -> List[Booking]:
        stmt = select(self.model).where(self.model.equipment_id == equipment_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_owner_id(self, session: AsyncSession, owner_id: int) -> List[Booking]:
        """
        Все брони на оборудование конкретного арендодателя.
        """
        stmt = (
            select(self.model)
            .join(Equipment, Equipment.id == self.model.equipment_id)
            .where(Equipment.user_id == owner_id)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    # ----------------------------------------------------------------------
    # STATUS UPDATE
    # ----------------------------------------------------------------------
    async def update_status(
        self,
        session: AsyncSession,
        booking_id: int,
        new_status: BookingStatus
    ) -> Optional[Booking]:

        booking = await self.get_by_id(session, booking_id)
        if not booking:
            return None

        booking.status = new_status
        await session.commit()
        await session.refresh(booking)
        return booking

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    async def delete(self, session: AsyncSession, booking_id: int) -> None:
        booking = await self.get_by_id(session, booking_id)
        if booking:
            await session.delete(booking)
            await session.commit()

    # ----------------------------------------------------------------------
    # SEARCH FOR OVERLAPS
    # ----------------------------------------------------------------------
    async def get_overlapping_bookings(
        self,
        session: AsyncSession,
        equipment_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Booking]:
        """
        Найти брони, даты которых пересекаются с указанным интервалом.
        """
        stmt = select(self.model).where(
            and_(
                self.model.equipment_id == equipment_id,
                self.model.date_from <= date_to,
                self.model.date_to >= date_from,
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def find_conflicting(
        self,
        session: AsyncSession,
        equipment_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Booking]:
        """
        Алиас для совместимости.
        """
        return await self.get_overlapping_bookings(session, equipment_id, date_from, date_to)
