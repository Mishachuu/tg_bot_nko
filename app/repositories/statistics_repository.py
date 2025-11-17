# app/repositories/statistics_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, case, text
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.equipment import Equipment, EquipmentStatus
from app.models.booking import Booking, BookingStatus
from app.models.user_app import AppUser

class StatisticsRepository:
    
    @staticmethod
    async def get_base_stats(session: AsyncSession) -> Dict[str, Any]:
        """Получить базовую статистику"""
        # Количество пользователей
        total_users_query = select(func.count(AppUser.id))
        total_users_result = await session.execute(total_users_query)
        total_users = total_users_result.scalar_one()
        
        # Количество арендодателей
        total_lessors_query = select(func.count(AppUser.id)).where(AppUser.is_lessor == True)
        total_lessors_result = await session.execute(total_lessors_query)
        total_lessors = total_lessors_result.scalar_one()
        
        # Количество оборудования
        total_equipment_query = select(func.count(Equipment.id))
        total_equipment_result = await session.execute(total_equipment_query)
        total_equipment = total_equipment_result.scalar_one()
        
        # Количество подтвержденных бронирований
        approved_bookings_query = select(func.count(Booking.id)).where(
            Booking.status == BookingStatus.CONFIRMED
        )
        approved_bookings_result = await session.execute(approved_bookings_query)
        approved_bookings = approved_bookings_result.scalar_one()
        
        # Количество отклоненных бронирований
        rejected_bookings_query = select(func.count(Booking.id)).where(
            Booking.status == BookingStatus.REJECTED
        )
        rejected_bookings_result = await session.execute(rejected_bookings_query)
        rejected_bookings = rejected_bookings_result.scalar_one()
        
        return {
            "total_users": total_users,
            "total_lessors": total_lessors,
            "total_equipment": total_equipment,
            "approved_bookings": approved_bookings,
            "rejected_bookings": rejected_bookings
        }
    
    @staticmethod
    async def get_popular_categories(session: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить популярные категории"""
        # Предполагаем, что у нас есть модель Category
        # Если её нет, можно адаптировать под текущую структуру
        
        # Временная реализация - возвращаем категории с количеством оборудования
        popular_categories_query = select(
            Equipment.category_id,
            func.count(Equipment.id).label('equipment_count'),
            func.count(Booking.id).label('booking_count')
        ).select_from(
            Equipment
        ).outerjoin(
            Booking, Equipment.id == Booking.equipment_id
        ).group_by(
            Equipment.category_id
        ).order_by(
            func.count(Booking.id).desc(),
            func.count(Equipment.id).desc()
        ).limit(limit)
        
        result = await session.execute(popular_categories_query)
        categories_data = result.all()
        
        return [
            {
                "category_id": category_id,
                "equipment_count": equipment_count,
                "booking_count": booking_count
            }
            for category_id, equipment_count, booking_count in categories_data
        ]
    
    @staticmethod
    async def get_popular_items(session: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить популярное оборудование"""
        popular_items_query = select(
            Equipment.id,
            Equipment.name,
            func.count(Booking.id).label('booking_count'),
            func.coalesce(func.sum(Booking.quantity), 0).label('total_quantity_booked')
        ).select_from(
            Equipment
        ).outerjoin(
            Booking, Equipment.id == Booking.equipment_id
        ).group_by(
            Equipment.id, Equipment.name
        ).order_by(
            func.count(Booking.id).desc(),
            func.coalesce(func.sum(Booking.quantity), 0).desc()
        ).limit(limit)
        
        result = await session.execute(popular_items_query)
        items_data = result.all()
        
        return [
            {
                "equipment_id": equipment_id,
                "equipment_name": equipment_name,
                "booking_count": booking_count,
                "total_quantity_booked": total_quantity_booked
            }
            for equipment_id, equipment_name, booking_count, total_quantity_booked in items_data
        ]
    
    @staticmethod
    async def get_advanced_stats(session: AsyncSession) -> Dict[str, Any]:
        """Получить расширенную статистику"""
        # Средний срок аренды (в днях)
        avg_rental_query = select(
            func.avg(
                func.extract('epoch', Booking.date_to - Booking.date_to) / 86400.0
            )
        ).where(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.date_to.isnot(None),
                Booking.date_from.isnot(None)
            )
        )
        
        avg_rental_result = await session.execute(avg_rental_query)
        avg_rental_duration = avg_rental_result.scalar_one()
        
        # Количество активных пользователей (с > 1 бронированием)
        active_users_query = select(
            func.count(func.distinct(Booking.user_id))
        ).select_from(
            select(
                Booking.user_id,
                func.count(Booking.id).label('booking_count')
            ).group_by(
                Booking.user_id
            ).having(
                func.count(Booking.id) > 1
            ).subquery()
        )
        
        active_users_result = await session.execute(active_users_query)
        active_users_count = active_users_result.scalar_one()
        
        # Общее количество дней аренды
        total_rental_days_query = select(
            func.coalesce(
                func.sum(
                    func.extract('epoch', Booking.date_to - Booking.date_from) / 86400.0
                ), 0
            )
        ).where(
            Booking.status == BookingStatus.CONFIRMED
        )
        
        total_rental_days_result = await session.execute(total_rental_days_query)
        total_rental_days = total_rental_days_result.scalar_one() or 0
        
        return {
            "avg_rental_duration_days": float(avg_rental_duration) if avg_rental_duration else None,
            "active_users_count": active_users_count,
            "total_rental_days": int(total_rental_days)
        }