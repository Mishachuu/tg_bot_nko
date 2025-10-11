from dataclasses import dataclass

@dataclass
class User:
    """
    Базовый класс для всех пользователей системы.
    
    Attributes:
        id (int): Уникальный идентификатор пользователя.
        name (str): Имя пользователя.
        tg_id (int): Telegram ID пользователя.
    """
    id: int
    name: str
    tg_id: int