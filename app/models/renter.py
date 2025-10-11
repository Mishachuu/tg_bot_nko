from dataclasses import dataclass
from models.user import User
from typing import List

@dataclass
class Renter(User):
    """
    Класс арендатора.
    
    Attributes:
        rented_items (list): Список объектов, арендованных пользователем.
        phone_numbers (list): Список контактных телефонов арендатора.
        emails (list): Список контактных email арендатора.
        city (str): Город проживания арендатора.
        score (float): Рейтинг арендатора.
    """
    rented_items: List[str]
    phone_numbers: List[str]
    emails: List[str]
    city: str
    score: float