# app/api/statistics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.api.dependencies import get_db
from app.services.statistics_service import StatisticsService
from app.api.schemas.statistics_schema import (
    BaseStatsResponse, CategoryStats, PopularItem, 
    AdvancedStats, StatisticsResponse
)

router = APIRouter(prefix="/statistics", tags=["statistics"])

def get_statistics_service() -> StatisticsService:
    return StatisticsService()

# Базовая статистика
@router.get("/base", response_model=BaseStatsResponse)
async def get_base_statistics(
    session: AsyncSession = Depends(get_db),
    statistics_service: StatisticsService = Depends(get_statistics_service)
):
    """Получить базовую статистику"""
    try:
        return await statistics_service.get_base_statistics(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статистики: {str(e)}")

# Популярные категории
@router.get("/popular/categories", response_model=List[CategoryStats])
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50, description="Количество категорий"),
    session: AsyncSession = Depends(get_db),
    statistics_service: StatisticsService = Depends(get_statistics_service)
):
    """Получить популярные категории оборудования"""
    try:
        return await statistics_service.get_popular_categories(session, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении категорий: {str(e)}")

# Популярное оборудование
@router.get("/popular/items", response_model=List[PopularItem])
async def get_popular_items(
    limit: int = Query(10, ge=1, le=50, description="Количество предметов"),
    session: AsyncSession = Depends(get_db),
    statistics_service: StatisticsService = Depends(get_statistics_service)
):
    """Получить популярное оборудование"""
    try:
        return await statistics_service.get_popular_items(session, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении оборудования: {str(e)}")

# Расширенная статистика
@router.get("/advanced", response_model=AdvancedStats)
async def get_advanced_statistics(
    session: AsyncSession = Depends(get_db),
    statistics_service: StatisticsService = Depends(get_statistics_service)
):
    """Получить расширенную статистику"""
    try:
        return await statistics_service.get_advanced_statistics(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении расширенной статистики: {str(e)}")

# Полная статистика
@router.get("/", response_model=StatisticsResponse)
async def get_complete_statistics(
    include_advanced: bool = Query(False, description="Включить расширенную статистику"),
    session: AsyncSession = Depends(get_db),
    statistics_service: StatisticsService = Depends(get_statistics_service)
):
    """Получить полную статистику"""
    try:
        return await statistics_service.get_complete_statistics(session, include_advanced)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении полной статистики: {str(e)}")