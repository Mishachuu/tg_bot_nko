from dataclasses import dataclass
from models.user import User
from models.equipment import Equipment
from typing import List
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column

class Publishing(StrEnum):
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
        phone_numbers (list): Список контактных телефонов арендодателя.
        emails (list): Список контактных email арендодателя.
        city (str): Город пользователя 
        score (float): Рейтинг арендодателя.
        rented_items (List[Equipment]): Список забронированного оборудования пользователем 
        equipment_list (List[Equipment]): Список оборудования, который выложил данный пользователь
    """
    
    phone_number: Mapped[str]
    email: Mapped[str]
    publish: Mapped[Publishing] = mapped_column(StrEnum(Publishing),default="blocked")

    city_id: Mapped[int]
    score: Mapped[float] = mapped_column(default=0)

    rented_items: List[Equipment]
    equipment_list: List[Equipment]


