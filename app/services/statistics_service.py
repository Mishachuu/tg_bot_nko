# app/services/statistics_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from app.repositories.statistics_repository import StatisticsRepository
from app.api.schemas.statistics_schema import (
    BaseStatsResponse, CategoryStats, PopularItem, 
    AdvancedStats, StatisticsResponse
)

class StatisticsService:
    
    def __init__(self):
        self.repository = StatisticsRepository()
    
    async def get_base_statistics(self, session: AsyncSession) -> BaseStatsResponse:
        """Получить базовую статистику"""
        base_stats = await self.repository.get_base_stats(session)
        return BaseStatsResponse(**base_stats)
    
    async def get_popular_categories(self, session: AsyncSession, limit: int = 10) -> List[CategoryStats]:
        """Получить популярные категории"""
        categories_data = await self.repository.get_popular_categories(session, limit)
        
        # Здесь можно добавить логику для получения названий категорий
        # если у вас есть соответствующая модель
        return [
            CategoryStats(
                category_id=cat["category_id"],
                category_name=cat['category_name'],
                equipment_count=cat["equipment_count"],
                booking_count=cat["booking_count"]
            )
            for cat in categories_data
        ]
    
    async def get_popular_items(self, session: AsyncSession, limit: int = 10) -> List[PopularItem]:
        """Получить популярное оборудование"""
        items_data = await self.repository.get_popular_items(session, limit)
        
        return [
            PopularItem(
                equipment_id=item["equipment_id"],
                equipment_name=item["equipment_name"],
                booking_count=item["booking_count"],
                total_quantity_booked=item["total_quantity_booked"]
            )
            for item in items_data
        ]
    
    async def get_advanced_statistics(self, session: AsyncSession) -> AdvancedStats:
        """Получить расширенную статистику"""
        advanced_stats = await self.repository.get_advanced_stats(session)
        return AdvancedStats(**advanced_stats)
    
    async def get_complete_statistics(
        self, 
        session: AsyncSession, 
        include_advanced: bool = False
    ) -> StatisticsResponse:
        """Получить полную статистику"""
        base_stats = await self.get_base_statistics(session)
        popular_categories = await self.get_popular_categories(session)
        popular_items = await self.get_popular_items(session)
        
        advanced_stats = None
        if include_advanced:
            advanced_stats = await self.get_advanced_statistics(session)
        
        return StatisticsResponse(
            base_stats=base_stats,
            popular_categories=popular_categories,
            popular_items=popular_items,
            advanced_stats=advanced_stats
        )