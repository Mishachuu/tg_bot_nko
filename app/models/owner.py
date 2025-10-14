from dataclasses import dataclass
from models.user import User
from typing import List

@dataclass
class Owner(User):
    """
    Класс арендодателя.
    
    Attributes:
        equipment_list (list): Список оборудования или недвижимости, принадлежащей арендодателю.
        phone_numbers (list): Список контактных телефонов арендодателя.
        emails (list): Список контактных email арендодателя.
        score (float): Рейтинг арендодателя.
    """
    equipment_list: List[str]
    phone_numbers: List[str]
    emails: List[str]
    score: float
