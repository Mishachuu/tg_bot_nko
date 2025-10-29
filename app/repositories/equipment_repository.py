# app/repositories/equipment_repository.py
from __future__ import annotations

from typing import Iterable, Sequence
from datetime import datetime

from sqlalchemy import insert, select, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql import Select, Update, Delete, Insert
from dataclasses import asdict
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import func
from app.helpers.gis_helper import calculate_distance
from app.models.equipment import Equipment


class EquipmentRepository:
    """
    Репозиторий инкапсулирует прямую работу с БД (CRUD-запросы).

    Ожидается, что где-то в слое инфраструктуры описана таблица `equipment_table`
    (SQLAlchemy Table) с колонками, соответствующими полям dataclass Equipment.
    Эту таблицу мы передаем в конструктор.

    Пример объявления (для понимания, не обязателен здесь):
    -----------------------------------------------------------------
    from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, LargeBinary, MetaData, Enum

    metadata = MetaData()

    equipment_table = Table(
        "equipment",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("name", String, nullable=True),
        Column("city_id", Integer, nullable=True),
        Column("landlord_id", Integer, nullable=True),
        Column("status", String, nullable=False),
        Column("photo", LargeBinary, nullable=True),   # либо String, если храните URL/file_id
        Column("category_id", Integer, nullable=True),
        Column("is_approved", Boolean, nullable=False, default=False),
        Column("description", String, nullable=True),
        Column("quantity", Integer, nullable=False, default=1),
        Column("created_at", DateTime, nullable=True),
    )
    -----------------------------------------------------------------
    """



    # ------------------- MAPPERS -------------------

    def _row_to_entity(self, row) -> Equipment:
        """Простой маппер строки результата в dataclass Equipment."""
        if row is None:
            return None
        d = dict(row._mapping)  # row -> dict
        
        # ОТЛАДКА: выводим все поля строки
        print(f"🔍 МАППИНГ СТРОКИ В Equipment:")
        print(f"   Все поля: {d}")
        print(f"   latitude: {d.get('latitude')} (тип: {type(d.get('latitude'))})")
        print(f"   longitude: {d.get('longitude')} (тип: {type(d.get('longitude'))})")
        
        # Приводим к типам из домена
        equipment = Equipment(
            id=d.get("id"),
            name=d.get("name"),
            city_id=d.get("city_id"),
            landlord_id=d.get("landlord_id"),
            category_id=d.get("category_id"),
            is_approved=bool(d.get("is_approved")),
            description=d.get("description"),
            quantity=int(d.get("quantity")) if d.get("quantity") is not None else 1,
            created_at=d.get("created_at"),
            latitude=d.get("latitude"),
            longitude=d.get("longitude")
        )
        
        print(f"   Результат Equipment: latitude={equipment.latitude}, longitude={equipment.longitude}")
        print(f"   Проверка условия: latitude is not None = {equipment.latitude is not None}")
        print(f"   Проверка условия: longitude is not None = {equipment.longitude is not None}")
        
        return equipment

    # ------------------- CRUD -------------------

    async def create(self, session: AsyncSession, equipment: Equipment) -> Equipment:
        """
        Создает запись и возвращает созданную сущность с новым ID.
        """
        # Подготавливаем словарь для INSERT
        payload = equipment.to_dict()
        # В БД лучше хранить photo как bytes или строку — сюда кладем как есть
        # created_at пусть прилетает снаружи; если None — ставим на уровне сервиса

        stmt: Insert = insert(self._t).values(payload).returning(self._t)
        res: Result = await session.execute(stmt)
        row = res.fetchone()
        # commit делаем в сервисе — чтобы можно было батчить операции
        return self._row_to_entity(row)

    async def get_by_id(self, session: AsyncSession, equipment_id: int) -> Equipment | None:
        stmt: Select = select(self._t).where(self._t.c.id == equipment_id)
        res: Result = await session.execute(stmt)
        row = res.fetchone()
        return self._row_to_entity(row)

    async def get_all(self, session: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[Equipment]:
        stmt: Select = select(self._t).order_by(self._t.c.id).limit(limit).offset(offset)
        res: Result = await session.execute(stmt)
        return [self._row_to_entity(r) for r in res.fetchall()]

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
        
        # Сначала получаем все оборудование категории
        stmt = (
            select(self._t)
            .where(self._t.c.category_id == category_id)
            .where(self._t.c.is_approved == True)
            .where(self._t.c.latitude.isnot(None))
            .where(self._t.c.longitude.isnot(None))
        )
        
        print(f"SQL запрос: {stmt}")
        
        res: Result = await session.execute(stmt)
        rows = res.fetchall()
        all_equipment = [self._row_to_entity(r) for r in rows]
        
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

    async def get_by_category(
        self, session: AsyncSession, category_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Equipment]:
        stmt: Select = (
            select(self._t)
            .where(self._t.c.category_id == category_id)
            .order_by(self._t.c.id)
            .limit(limit)
            .offset(offset)
        )
        res: Result = await session.execute(stmt)
        return [self._row_to_entity(r) for r in res.fetchall()]

    async def get_by_city(
        self, session: AsyncSession, city_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Equipment]:
        stmt: Select = (
            select(self._t)
            .where(self._t.c.city_id == city_id)
            .order_by(self._t.c.id)
            .limit(limit)
            .offset(offset)
        )
        res: Result = await session.execute(stmt)
        return [self._row_to_entity(r) for r in res.fetchall()]

    async def update(self, session: AsyncSession, equipment_id: int, fields: dict) -> Equipment | None:
        """
        Обновляет указанные поля. Возвращает обновленную сущность, либо None.
        """
        if not fields:
            # Нечего обновлять — просто вернуть текущее состояние
            return await self.get_by_id(session, equipment_id)

        # Приведение статуса к строке, если передали Enum
        status = fields.get("status")
        if isinstance(status, RentalStatus):
            fields["status"] = status.value

        # created_at приводить не нужно — предполагается datetime
        stmt: Update = (
            sql_update(self._t)
            .where(self._t.c.id == equipment_id)
            .values(**fields)
            .returning(self._t)
        )
        res: Result = await session.execute(stmt)
        row = res.fetchone()
        return self._row_to_entity(row)

    async def delete(self, session: AsyncSession, equipment_id: int) -> bool:
        """
        Удаляет запись. Возвращает True, если что-то удалили.
        """
        stmt: Delete = sql_delete(self._t).where(self._t.c.id == equipment_id)
        res = await session.execute(stmt)
        # rowcount у async + Core может быть None у некоторых драйверов, но чаще OK
        return (res.rowcount or 0) > 0