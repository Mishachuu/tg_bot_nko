# app/repositories/equipment_repository.py
from __future__ import annotations

from typing import Iterable, Sequence
from datetime import datetime

from sqlalchemy import insert, select, update as sql_update, delete as sql_delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql import Select, Update, Delete, Insert
from dataclasses import asdict
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import func
from app.helpers.gis_helper import calculate_distance
from app.models.equipment import Equipment
from typing import List, Optional


class EquipmentRepository:
    """
    Репозиторий инкапсулирует прямую работу с БД (CRUD-запросы).
    """
    def __init__(self):
        self.model = Equipment
    # ------------------- CRUD -------------------

    async def add_equipment(self, session: AsyncSession, equipment: Equipment) -> Equipment:
        """
        Создает запись и возвращает созданную сущность с новым ID.
        """
        session.add(equipment)
        await session.commit()
        await session.refresh(equipment)
        return equipment
    
    async def get_all(self, session: AsyncSession, limit: int = 100, offset: int = 0):
        """Return:  List[Equipment]"""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        res = await session.execute(select(self.model).where(self.model.id == equipment_id))
        equipment = res.scalars().one_or_none()
        return equipment 

    async def get_by_user_id(self, session: AsyncSession, user_id: int):
        res = await session.execute(select(self.model).where(self.model.user_id == user_id))
        equipment = res.scalars().all()
        return equipment
        
    async def get_by_category_id(self, session: AsyncSession, category_id: int, limit: int = 100, offset: int = 0):
        """Получить оборудование по категории"""
        stmt = (
            select(self.model)
            .where(self.model.category_id == category_id)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(self, session: AsyncSession, equipment_id: int, changes: dict) -> Equipment | None:
        """
        Обновляет указанные поля. Возвращает обновленную сущность, либо None.
        """
        # 1) Получаем объект
        res = await session.execute(select(self.model).where(self.model.id == equipment_id))
        equipment = res.scalars().one_or_none()
        if equipment is None:
            return None

        # 2) Применяем изменения (changes — dict с полями, которые нужно обновить)
        for k, v in changes.items():
            if hasattr(equipment, k):
                setattr(equipment, k, v)

        # 3) Сохраняем измененя
        await session.commit()
        await session.refresh(equipment)  # подтянуть актуальные поля
        return equipment

    async def delete(self, session: AsyncSession, equipment_id: int) -> bool:
        res = await session.execute(select(self.model).where(self.model.id == equipment_id))
        user = res.scalars().one_or_none()
        if user is None:
            return False

        await session.delete(user)
        try:
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            raise
    
    # ===== Это переписать ===== 
    async def get_by_location(
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
        Возвращает оборудование в пределах указанного радиуса (в км) от заданной точки.
        Используется приближённая формула расстояния.
        """
        # Haversine через SQL выражения (PostgreSQL/MySQL/SQLite — все поддерживают функции sin/cos/acos)
        lat1 = radians(latitude)
        lon1 = radians(longitude)

        lat_col = func.radians(self._t.c.latitude)
        lon_col = func.radians(self._t.c.longitude)

        # Формула: 6371 — радиус Земли в км
        distance_expr = 6371 * func.acos(
            func.cos(lat1) * func.cos(lat_col) * func.cos(lon_col - lon1)
            + func.sin(lat1) * func.sin(lat_col)
        )

        stmt = (
            select(self._t)
            .where(distance_expr <= radius_km)
            .where(self._t.c.is_approved == True)
            .where(self._t.c.latitude.isnot(None))
            .where(self._t.c.longitude.isnot(None))
            .order_by(distance_expr)
            .limit(limit)
            .offset(offset)
        )

        res: Result = await session.execute(stmt)
        rows = res.fetchall()
        return [self._row_to_entity(r) for r in rows]

    async def get_by_category_and_location(
        self,
        session: AsyncSession,
        category_id: int,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> list[Equipment]:
        """
        Получаем все оборудование категории, затем фильтруем по расстоянию в коде.
        """
        print(f"🔍 ПОИСК: категория={category_id}, локация=({latitude}, {longitude}), радиус={radius_km}км")
        
        # Сначала получаем все оборудование категории с помощью ORM
        stmt = (
            select(self.model)
            .where(self.model.category_id == category_id)
            .where(self.model.is_approved == True)
            .where(self.model.latitude.isnot(None))
            .where(self.model.longitude.isnot(None))
        )
        
        print(f"SQL запрос: {stmt}")
        
        result = await session.execute(stmt)
        all_equipment = result.scalars().all()
        
        print(f"📊 Всего оборудования в категории {category_id}: {len(all_equipment)}")
        
        # ВЫВОДИМ КАЖДЫЙ ЭЛЕМЕНТ ДЛЯ ОТЛАДКИ
        for i, eq in enumerate(all_equipment):
            print(f"  [{i}] Оборудование ID {eq.id}: {eq.name}")
            print(f"      Категория: {eq.category_id}, Одобрено: {eq.is_approved}")
            print(f"      Координаты: ({eq.latitude}, {eq.longitude})")
            print(f"      Проверка координат: lat not None={eq.latitude is not None}, lon not None={eq.longitude is not None}")
        
        # Фильтруем по расстоянию
        filtered_equipment = []
        for eq in all_equipment:
            print(f"🎯 ОБРАБОТКА оборудования {eq.id}:")
            
            # ПРОВЕРКА КООРДИНАТ
            has_coords = eq.latitude is not None and eq.longitude is not None
            print(f"   has_coords = {has_coords}")
            
            if has_coords:
                distance = calculate_distance(latitude, longitude, eq.latitude, eq.longitude)
                print(f"\t📏 Расстояние: {distance:.1f} км")
                print(f"\t📏 Радиус поиска: {radius_km} км")
                print(f"\t📏 Условие: distance <= radius_km = {distance <= radius_km}")
                
                if distance <= radius_km:
                    filtered_equipment.append(eq)
                    print(f"\t✅ ДОБАВЛЕНО в результат")
                else:
                    print(f"\t❌ ЗА ПРЕДЕЛАМИ радиуса")
            else:
                print(f"\t⚠️ НЕТ КООРДИНАТ")
        
        print(f"🎯 ИТОГО отфильтровано по локации: {len(filtered_equipment)}")
        
        # Применяем limit и offset
        result = filtered_equipment[offset:offset + limit]
        print(f"📦 ФИНАЛЬНЫЙ результат после limit/offset: {len(result)} записей")
        return result
    
    async def list_by_owner(self, session: AsyncSession, owner_id: int, limit: int = 100, offset: int = 0):
        """Получить оборудование по владельцу"""
        stmt = (
            select(self.model)
            .where(self.model.user_id == owner_id)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_total_count(self, session: AsyncSession) -> int:
        """Получить общее количество записей"""
        stmt = select(func.count(Equipment.id))
        result = await session.execute(stmt)
        return result.scalar()

    async def get_by_approval_status(
        self, 
        session: AsyncSession, 
        is_approved: bool,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        """Получить по статусу одобрения"""
        stmt = (
            select(self.model)
            .where(self.model.is_approved == is_approved)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def search(
        self,
        session: AsyncSession,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Equipment]:
        """Расширенный поиск"""
        stmt = select(self.model)
        
        if category_id is not None:
            stmt = stmt.where(self.model.category_id == category_id)
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if is_approved is not None:
            stmt = stmt.where(self.model.is_approved == is_approved)
        if name:
            stmt = stmt.where(self.model.name.ilike(f"%{name}%"))
        
        stmt = stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()