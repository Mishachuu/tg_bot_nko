from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class BaseStatsResponse(BaseModel):
    total_users: int
    total_lessors: int
    total_equipment: int
    approved_bookings: int
    rejected_bookings: int

class CategoryStats(BaseModel):
    category_id: int
    category_name: Optional[str]
    equipment_count: int
    booking_count: int

class PopularItem(BaseModel):
    equipment_id: int
    equipment_name: Optional[str]
    booking_count: int
    total_quantity_booked: int

class AdvancedStats(BaseModel):
    avg_rental_duration_days: Optional[float]
    active_users_count: int  # пользователи с > 1 бронированием
    total_rental_days: int

class StatisticsResponse(BaseModel):
    base_stats: BaseStatsResponse
    popular_categories: List[CategoryStats]
    popular_items: List[PopularItem]
    advanced_stats: Optional[AdvancedStats] = None