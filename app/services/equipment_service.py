from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.equipment import Equipment, EquipmentStatus
from app.repositories.equipment_repository import EquipmentRepository
from app.services.booking_service import BookingService


class EquipmentService:
    def __init__(self, repo: EquipmentRepository, booking_service: BookingService):
        self._repo = repo
        self._booking_service = booking_service

    # Правила/валидации
    def _apply_defaults_on_create(self, eq: Equipment) -> Equipment:
        """
        Бизнес-правила при создании:
        - статус всегда MODERATION
        - created_at проставляем, если не задан
        - quantity минимум 1
        """
        eq.status = EquipmentStatus.MODERATION
        eq.created_at = eq.created_at or datetime.now(tz=timezone.utc).replace(tzinfo=None)
        if not eq.quantity or eq.quantity < 1:
            eq.quantity = 1
        return eq

    # Основные CRUD методы
    async def create_equipment(self, session: AsyncSession, equipment: Equipment) -> Equipment:
        equipment = self._apply_defaults_on_create(equipment)
        created = await self._repo.add_equipment(session, equipment)
        await session.commit()
        return created

    async def get_equipment(self, session: AsyncSession, equipment_id: int) -> Optional[Equipment]:
        return await self._repo.get_by_id(session, equipment_id)

    async def list_equipment(self, session: AsyncSession, *, limit: int = 100, offset: int = 0) -> List[Equipment]:
        return await self._repo.get_all(session, limit=limit, offset=offset)

    async def update_equipment(self, session: AsyncSession, equipment_id: int, **fields) -> Optional[Equipment]:
        """
        Обновление с валидацией:
        - quantity не даем опустить ниже 1
        - автоматическая конвертация строкового status в Enum
        """
        if "quantity" in fields and fields["quantity"] is not None and fields["quantity"] < 1:
            fields["quantity"] = 1
            
        # Конвертируем строковый status в Enum если нужно
        if "status" in fields and isinstance(fields["status"], str):
            fields["status"] = EquipmentStatus(fields["status"])

        updated = await self._repo.update(session, equipment_id, fields)
        await session.commit()
        return updated

    async def delete_equipment(self, session: AsyncSession, equipment_id: int) -> bool:
        deleted = await self._repo.delete(session, equipment_id)
        await session.commit()
        return deleted

    async def approve_equipment(
    self, 
    session: AsyncSession, 
    equipment_id: int
) -> Optional[Equipment]:
        """Одобрить оборудование"""
        changes = {
            "status": EquipmentStatus.APPROVED,
            "moderated_at": datetime.now(),
            "rejection_reason": None,
        }
        return await self._repo.update(session, equipment_id, changes)

    async def reject_equipment(
        self, 
        session: AsyncSession, 
        equipment_id: int, 
        reason: str = ""
    ) -> Optional[Equipment]:
        """Отклонить оборудование с причиной"""
        changes = {
            "status": EquipmentStatus.REJECTED,
            "moderated_at": datetime.now(),
            "rejection_reason": reason,
        }
        return await self._repo.update(session, equipment_id, changes)

    # ===== ПОИСК И ФИЛЬТРАЦИЯ =====
    
    async def find_by_category(
        self, session: AsyncSession, category_id: int, *, limit: int = 100, offset: int = 0
    ) -> List[Equipment]:
        return await self._repo.get_by_category_id(session, category_id, limit=limit, offset=offset)

    async def find_by_location(
        self,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
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
    ) -> List[Equipment]:
        eq_list = await self._repo.get_by_category_and_location(
            session, 
            category_id, 
            latitude=latitude, 
            longitude=longitude, 
            radius_km=radius_km,
            limit=limit, 
            offset=offset
        )
        
        available = []
        for eq in eq_list:
            if self._booking_service:
                is_free = await self._booking_service.is_equipment_available(session, eq.id, date_from, date_to)
                if not is_free:
                    continue
            available.append(eq)

        return available
    
    async def list_by_owner(self, session: AsyncSession, owner_id: int, limit: int = 100, offset: int = 0) -> List[Equipment]:
        return await self._repo.list_by_owner(session, owner_id, limit=limit, offset=offset)
    
    # ===== УДОБНЫЕ МЕТОДЫ ДЛЯ API =====
    
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
        equipment = Equipment(
            name=name,
            user_id=user_id,
            category_id=category_id,
            description=description,
            quantity=quantity,
            latitude=latitude,
            longitude=longitude
        )
        return await self.create_equipment(session, equipment)

    async def get_total_count(self, session: AsyncSession) -> int:
        return await self._repo.get_total_count(session)

    async def get_equipment_by_status(
        self, 
        session: AsyncSession, 
        status: EquipmentStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        return await self._repo.get_by_status(session, status, limit=limit, offset=offset)

    async def get_awaiting_moderation(
        self, 
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        return await self._repo.get_awaiting_moderation(session, limit=limit, offset=offset)

    async def get_approved_equipment(
        self, 
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        return await self._repo.get_approved_equipment(session, limit=limit, offset=offset)

    async def search_equipment(
        self,
        session: AsyncSession,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[EquipmentStatus] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        return await self._repo.search(
            session,
            category_id=category_id,
            user_id=user_id,
            status=status,
            name=name,
            limit=limit,
            offset=offset
        )

    async def update_status(
        self, 
        session: AsyncSession, 
        equipment_id: int, 
        status: EquipmentStatus,
        moderator_id: Optional[int] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[Equipment]:
        """Обновление статуса с дополнительной информацией"""
        changes = {
            "status": status,
            "moderated_at": datetime.now(),
        }
        
        if moderator_id:
            changes["moderated_by"] = moderator_id
            
        if status == EquipmentStatus.REJECTED and rejection_reason:
            changes["rejection_reason"] = rejection_reason
        elif status == EquipmentStatus.APPROVED:
            changes["rejection_reason"] = None
        
        return await self.update(session, equipment_id, changes)

    # ===== УТИЛИТЫ =====
    
    async def get_equipment_stats(self, session: AsyncSession) -> dict:
        """Получить статистику по оборудованию"""
        total = await self.get_total_count(session)
        moderation = len(await self.get_awaiting_moderation(session, limit=1000))
        approved = len(await self.get_approved_equipment(session, limit=1000))
        
        return {
            "total": total,
            "moderation": moderation,
            "approved": approved,
            "rejected": total - moderation - approved
        }