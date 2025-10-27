from dataclasses import dataclass
from models.equipment import Equipment
from typing import List
#Для sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column

@dataclass
class User:
    """
    Attributes:
        id (int): Уникальный идентификатор пользователя.
        name (str): Имя пользователя.
        tg_id (int): Telegram ID пользователя.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    tg_id: Mapped[int] = mapped_column(unique=True) # по нему вроде можно узнать username tg 


