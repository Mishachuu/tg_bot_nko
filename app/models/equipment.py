from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import StrEnum

class RentalStatus(StrEnum):
    AVAILABLE = "available"
    BOOKED = "booked"
    IN_USE = "in_use"
    RETURNED = "returned"

@dataclass
class Equipment:
    """
    Atribute:
        user_id (int): пользователь который разместил оборудование
    """
    id: int = None
    name: Optional[str] = None
    city_id: Optional[int] = None
    user_id: Optional[int] = None
    status: RentalStatus = RentalStatus.AVAILABLE
    category_id: Optional[int] = None
    is_approved: bool = False
    description: Optional[str] = None
    quantity: int = 1
    created_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "city_id": self.city_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "category_id": self.category_id,
            "is_approved": self.is_approved,
            "description": self.description,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }