from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking_repository import BookingRepository
from app.repositories.equipment_repository import EquipmentRepository
from app.models.booking import Booking
from app.models.enums import BookingStatus


class BookingService:
    def __init__(self, repo: BookingRepository):
        self.repo = repo
        self.equipment_repo = EquipmentRepository()

    async def create_booking(
        self,
        session: AsyncSession,
        equipment_id: int,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
        quantity: int = 1,
    ) -> Booking:
        """
        Создает новое бронирование в статусе PENDING.
        Проверяет возможность бронирования по количеству и датам.
        """
        if date_to < date_from:
            raise ValueError("Дата окончания брони не может быть раньше даты начала")

        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        # Проверяем доступность оборудования по количеству
        is_available = await self.is_equipment_available(
            session, equipment_id, date_from, date_to, required_quantity=quantity
        )
        if not is_available:
            raise ValueError("Недостаточно свободных единиц оборудования на эти даты")

        booking_data = {
            "equipment_id": equipment_id,
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
            "quantity": quantity,
            "status": BookingStatus.PENDING,
        }

        return await self.repo.create(session, booking_data)


    async def change_status(
        self,
        session: AsyncSession,
        booking_id: int,
        new_status: BookingStatus,
    ) -> Optional[Booking]:
        """
        Обновить статус бронирования:
        ACCEPTED — подтверждено
        DECLINED — отклонено
        CANCELED — отменено
        """
        if new_status not in (
            BookingStatus.ACCEPTED,
            BookingStatus.DECLINED,
            BookingStatus.CANCELED,
        ):
            raise ValueError("Недопустимый статус бронирования")

        return await self.repo.update_status(session, booking_id, new_status)

    async def get_booking(self, session: AsyncSession, booking_id: int) -> Optional[Booking]:
        return await self.repo.get_by_id(session, booking_id)

    async def list_bookings(self, session: AsyncSession) -> List[Booking]:
        return await self.repo.list(session)

    async def get_bookings_for_equipment(self, session: AsyncSession, equipment_id: int) -> List[Booking]:
        return await self.repo.get_by_equipment_id(session, equipment_id)

    async def get_user_bookings(self, session: AsyncSession, user_id: int) -> List[Booking]:
        """Все брони, созданные арендатором"""
        return await self.repo.get_by_user_id(session, user_id)

    async def get_owner_bookings(self, session: AsyncSession, owner_id: int) -> List[Booking]:
        """Все брони на оборудование арендодателя"""
        return await self.repo.get_by_owner_id(session, owner_id)


    async def is_equipment_available(
        self,
        session: AsyncSession,
        equipment_id: int,
        date_from: datetime,
        date_to: datetime,
        required_quantity: int = 1,
    ) -> bool:
        """
        Проверяет, хватает ли свободных единиц оборудования.
        Учитываются только брони со статусами PENDING и ACCEPTED.
        """
        equipment = await self.equipment_repo.get_by_id(session, equipment_id)
        if not equipment:
            return False

        conflicts = await self.repo.find_conflicting(session, equipment_id, date_from, date_to)

        active = [
            b for b in conflicts
            if b.status in (BookingStatus.PENDING, BookingStatus.ACCEPTED)
        ]

        used_quantity = sum(b.quantity for b in active)

        return (used_quantity + required_quantity) <= equipment.quantity
    
    async def get_available_quantity(self, session, equipment_id, date_from, date_to):
        equipment = await self.equipment_repo.get_by_id(session, equipment_id)
        conflicts = await self.repo.find_conflicting(session, equipment_id, date_from, date_to)

        active = [
            b for b in conflicts
            if b.status in (BookingStatus.PENDING, BookingStatus.ACCEPTED)
        ]

        used = sum(b.quantity for b in active)
        return equipment.quantity - used

