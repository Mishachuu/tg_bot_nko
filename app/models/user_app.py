from dataclasses import dataclass
from app.models.user import User
from app.models.equipment import Equipment
from typing import List
from enum import StrEnum,Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

class Publishing(str, Enum):
    """
    BLOCKED - Заблокированно
    REQUESTED - Запрос отправлен
    REJECTED - Отклонено
    APPROVED - Принято
    """
    BLOCKED = "blocked"
    REQUESTED = "requested"
    REJECTED = "rejected"
    APPROVED = "approved"

@dataclass
class AppUser(User):
    """
    Attributes:
        phone_number (str): телефон арендодателя.
        email (str): email арендодателя.
        city (str): Город пользователя 
        score (float): Рейтинг арендодателя.
        rented_items (List[Equipment]): Список забронированного оборудования пользователем 
        equipment_list (List[Equipment]): Список оборудования, который выложил данный пользователь
    """

    #rented_items: List[Equipment]
    #equipment_list: List[Equipment]
    
    email: Mapped[str] = mapped_column(nullable=True)
    publish: Mapped[Publishing] = mapped_column(
        SQLEnum("blocked", "requested", "rejected", "approved", name="publishing_enum"),
        default="blocked")
    phone_number: Mapped[str] = mapped_column(nullable=True)

    city_id: Mapped[int] = mapped_column(nullable=True)
    score: Mapped[float] = mapped_column(default=0)


