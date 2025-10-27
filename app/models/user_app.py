from dataclasses import dataclass
from models.user import User
from models.equipment import Equipment
from typing import List

from sqlalchemy.orm import Mapped, mapped_column

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
    allow_pub: Mapped[bool] = mapped_column(default=False)

    city: Mapped[str]
    score: Mapped[float] = mapped_column(default=0)

    rented_items: List[Equipment]
    equipment_list: List[Equipment]


