from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

@dataclass
class Equipment(Base):
    __tablename__ = "equipments"
    """
    Atribute:
        user_id (int): пользователь который разместил оборудование
        is_approved (bool): Поле которые так же проставляет модерация/адин (!! В дальнейшем передеалть под Enum !!)
        is_publish (bool): Если пользлватеоль удаляет объявление оно просто скрыватся но не удаляется удаилть объявление может только модератор/админ
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    city_id: Mapped[int] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(nullable=True)
    is_approved: Mapped[bool] = mapped_column(default=False)
    is_publish: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)

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