from __future__ import annotations
from enum import StrEnum
from dataclasses import dataclass, asdict
from datetime import datetime

class RentalStatus(StrEnum):
    AVAILABLE = "available"
    BOOKED = "booked"
    IN_USE = "in_use"
    RETURNED = "returned"

@dataclass(slots=True)
class Equipment:
    id: int | None = None
    name: str | None = None
    city_id: int | None = None
    landlord_id: int | None = None
    status: RentalStatus = RentalStatus.AVAILABLE
    photo_url: str | None = None

    category_id: int | None = None
    is_approved: bool = False
    description: str | None = None
    quantity: int = 1
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        """
        Обходит весь объект и приводит его к словарю
        """
        d = asdict(self)
        d["status"] = self.status.value
        d["created_at"] = self.created_at.isoformat() if self.created_at else None
        return d