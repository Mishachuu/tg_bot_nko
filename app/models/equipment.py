from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SQLEnum, ForeignKey
from app.db.base import Base

class EquipmentStatus(Enum):
    MODERATION = "moderation"    # На модерации
    APPROVED = "approved"        # Одобрено
    REJECTED = "rejected"       # Отклонено

class Equipment(Base):
    __tablename__ = "equipments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )

    category: Mapped["Category"] = relationship("Category", lazy="joined")

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None

    status: Mapped[str] = mapped_column(
        SQLEnum(EquipmentStatus), 
        default=EquipmentStatus.MODERATION,
        nullable=False
    )
    description: Mapped[str] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    rejection_reason: Mapped[str] = mapped_column(nullable=True)
    moderated_at: Mapped[datetime] = mapped_column(nullable=True)
    moderated_by: Mapped[int] = mapped_column(nullable=True)

    @property
    def display_status(self) -> str:
        status_map = {
            EquipmentStatus.MODERATION: "На модерации",
            EquipmentStatus.APPROVED: "Одобрено", 
            EquipmentStatus.REJECTED: "Отклонено",
        }
        return status_map.get(EquipmentStatus(self.status), "Неизвестно")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "status": self.status.value,
            "display_status": self.display_status,
            "description": self.description,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rejection_reason": self.rejection_reason,
            "moderated_at": self.moderated_at,
            "moderated_by": self.moderated_by,
        }