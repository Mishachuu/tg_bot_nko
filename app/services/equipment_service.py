# app/services/equipment_service.py
from __future__ import annotations
from typing import List, Optional

from typing import Iterable
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment, RentalStatus
from app.repositories.equipment_repository import EquipmentRepository
from app.services.booking_service import BookingService


class EquipmentService:
    """
    Сервисный слой: инкапсулирует бизнес-логику и транзакционные решения.
    Этим слоем пользуются боты и будущий сайт — он не знает SQL и таблиц.
    """

    def __init__(self, repo: EquipmentRepository, booking_service: BookingService):
        self._repo = repo
        self._booking_service = booking_service

    # Правила/валидации

    def _apply_defaults_on_create(self, eq: Equipment) -> Equipment:
        """
        Бизнес-правила при создании:
        - is_approved всегда False
        - статус всегда AVAILABLE
        - created_at проставляем, если не задан
        - quantity минимум 1
        """
        eq.is_approved = False
        eq.status = RentalStatus.AVAILABLE
        eq.created_at = eq.created_at or datetime.now(tz=timezone.utc).replace(tzinfo=None)  # храним naive UTC
        if not eq.quantity or eq.quantity < 1:
            eq.quantity = 1
        return eq

    # Сервисные методы 

    async def create_equipment(self, session: AsyncSession, equipment: Equipment) -> Equipment:
        """
        Создать оборудование с бизнес-правилами.
        """
        equipment = self._apply_defaults_on_create(equipment)
        created = await self._repo.create(session, equipment)
        await session.commit()  # фиксируем транзакцию сразу после создания
        return created

    async def get_equipment(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        return await self._repo.get_by_id(session, equipment_id)

    async def list_equipment(self, session: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[Equipment]:
        return await self._repo.get_all(session, limit=limit, offset=offset)

    async def find_by_category(
        self, session: AsyncSession, category_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Equipment]:
        return await self._repo.get_by_category(session, category_id, limit=limit, offset=offset)

    async def find_by_city(
        self, session: AsyncSession, city_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Equipment]:
        return await self._repo.get_by_city(session, city_id, limit=limit, offset=offset)

    async def update_equipment(self, session: AsyncSession, equipment_id: int, **fields) -> Equipment | None:
        """
        Обновление с простыми правилами:
        - если передали status как Enum — конвертируем в строку (репозиторий тоже это делает, но пусть будет явно)
        - quantity не даем опустить ниже 1
        """
        if "quantity" in fields and fields["quantity"] is not None and fields["quantity"] < 1:
            fields["quantity"] = 1

        updated = await self._repo.update(session, equipment_id, fields)
        await session.commit()
        return updated

    async def delete_equipment(self, session: AsyncSession, equipment_id: int) -> bool:
        deleted = await self._repo.delete(session, equipment_id)
        await session.commit()
        return deleted

    #  Примеры мини-бизнес-операций

    async def approve(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        """Простое одобрение карточки администратором."""
        updated = await self._repo.update(session, equipment_id, {"is_approved": True})
        await session.commit()
        return updated

    async def set_status(self, session: AsyncSession, equipment_id: int, status: RentalStatus) -> Equipment | None:
        """
        Безопасная смена статуса (минимальная проверка).
        Здесь можно расширить логику (например, запрещать переходы).
        """
        updated = await self._repo.update(session, equipment_id, {"status": status.value})
        await session.commit()
        return updated
    
    async def find_available_by_category_and_date(
        self,
        session: AsyncSession,
        category_id: int,
        date_from: datetime,
        date_to: datetime,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> list[Equipment]:
        """
        Возвращает оборудование выбранной категории, свободное в диапазоне дат.
        """
        eq_list = await self._repo.get_by_category(session, category_id, limit=limit, offset=offset)
        available = []

        for eq in eq_list:
            if eq.status != RentalStatus.AVAILABLE:
                continue
            if self._booking_service:
                is_free = await self._booking_service.is_equipment_available(session, eq.id, date_from, date_to)
                if not is_free:
                    continue
            available.append(eq)

        return available