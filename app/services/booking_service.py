from datetime import datetime
from app.repositories.booking_repository import BookingRepository


class BookingService:
    def __init__(self, repo: BookingRepository):
        self.repo = repo

    async def create_booking(self, session, equipment_id: int, user_id: int, date_from: datetime, date_to: datetime):
        if date_to < date_from:
            raise ValueError("Дата окончания брони не может быть раньше даты начала")

        existing = await self.repo.get_overlapping_bookings(session, equipment_id, date_from, date_to)
        if existing:
            raise ValueError("Выбранное оборудование уже забронировано на эти даты")

        booking = {
            "equipment_id": equipment_id,
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
        }

        await self.repo.create(session, booking)
        await session.flush()
        return booking

    async def list_bookings(self, session):
        return await self.repo.list(session)

    async def get_bookings_for_equipment(self, session, equipment_id: int):
        return await self.repo.get_by_equipment(session, equipment_id)

    async def is_equipment_available(self, session, equipment_id: int, date_from: datetime, date_to: datetime) -> bool:
        """Проверяет, свободно ли оборудование на выбранные даты"""
        conflicts = await self.repo.find_conflicting(session, equipment_id, date_from, date_to)
        return len(conflicts) == 0
