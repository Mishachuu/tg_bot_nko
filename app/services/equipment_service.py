
from __future__ import annotations
from typing import List, Optional

from typing import Iterable
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment
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
        # eq.is_approved = False
        # eq.status = RentalStatus.AVAILABLE
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
        created = await self._repo.add_equipment(session, equipment)
        await session.commit()  # фиксируем транзакцию сразу после создания
        return created

    async def get_equipment(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        return await self._repo.get_by_id(session, equipment_id)

    async def list_equipment(self, session: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[Equipment]:
        return await self._repo.get_all(session, limit=limit, offset=offset)

    async def find_by_category(
        self, session: AsyncSession, category_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Equipment]:
        return await self._repo.get_by_category_id(session, category_id)

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
    
    async def approve(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        """Простое одобрение карточки администратором."""
        updated = await self._repo.update(session, equipment_id, {"is_approved": True})
        await session.commit()
        return updated

    async def set_status(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        """
        Безопасная смена статуса (минимальная проверка).
        Здесь можно расширить логику (например, запрещать переходы).
        """
        updated = await self._repo.update(session, equipment_id)
        await session.commit()
        return updated
    
    async def find_by_location(
        self,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> list[Equipment]:
        """
        Возвращает список оборудования поблизости от указанных координат.
        """
        return await self._repo.get_by_location(
            session,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
            offset=offset,
        )
    
    async def find_available_by_category_date_and_location(
        self,
        session: AsyncSession,
        category_id: int,
        date_from: datetime,
        date_to: datetime,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> list[Equipment]:
        """
        Возвращает оборудование выбранной категории, свободное в диапазоне дат
        и находящееся в указанном радиусе.

        Учитываются:
            - количество свободных единиц оборудования
            - статусы бронирований (pending, accepted)
        """
        # Получаем оборудование по категории и локации
        eq_list = await self._repo.get_by_category_and_location(
            session,
            category_id,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
            offset=offset
        )

        available: list[Equipment] = []

        # Проверяем доступность каждого оборудования
        for eq in eq_list:
            # Проверяем, доступна ли хотя бы 1 единица оборудования
            is_free = await self._booking_service.is_equipment_available(
                session,
                equipment_id=eq.id,
                date_from=date_from,
                date_to=date_to,
                required_quantity=1
            )
            if is_free:
                available.append(eq)

        return available
    
    async def list_by_owner(self, session: AsyncSession, owner_id: int, limit: int = 100, offset: int = 0):
        return await self._repo.list_by_owner(session, owner_id, limit=limit, offset=offset)

    async def set_publish(self, session, equipment_id: int, is_publish: bool):
        updated = await self._repo.set_publish(session, equipment_id, is_publish)
        await session.commit()
        return updated
    
    async def create_equipment_from_params(
        self, 
        session: AsyncSession,
        name: str,
        user_id: int,
        category_id: int,
        description: Optional[str] = None,
        quantity: int = 1,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Equipment:
        """Создать оборудование с параметрами (для API)"""
        equipment = Equipment(
            name=name,
            user_id=user_id,
            category_id=category_id,
            description=description,
            quantity=quantity,
            latitude=latitude,
            longitude=longitude,
            is_approved=False,
            is_publish=False
        )
        return await self.create_equipment(session, equipment)

    async def get_total_count(self, session: AsyncSession) -> int:
        """Получить общее количество оборудования"""
        return await self._repo.get_total_count(session)

    async def get_equipment_by_approval_status(
        self, 
        session: AsyncSession, 
        is_approved: bool,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        """Получить оборудование по статусу одобрения"""
        return await self._repo.get_by_approval_status(session, is_approved, limit=limit, offset=offset)

    async def get_equipment_by_publish_status(
        self, 
        session: AsyncSession, 
        is_publish: bool,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        """Получить оборудование по статусу публикации"""
        return await self._repo.get_by_publish_status(session, is_publish, limit=limit, offset=offset)

    async def search_equipment(
        self,
        session: AsyncSession,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        is_publish: Optional[bool] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        """Расширенный поиск оборудования"""
        return await self._repo.search(
            session,
            category_id=category_id,
            user_id=user_id,
            is_approved=is_approved,
            is_publish=is_publish,
            name=name,
            limit=limit,
            offset=offset
        )

    async def approve_with_status(
        self, 
        session: AsyncSession, 
        equipment_id: int, 
        is_approved: bool
    ) -> Equipment | None:
        """Обновить статус одобрения с указанием статуса"""
        updated = await self._repo.update(session, equipment_id, {"is_approved": is_approved})
        await session.commit()
        return updated