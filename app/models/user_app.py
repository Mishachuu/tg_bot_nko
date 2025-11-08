from enum import Enum

from app.db.base import Base
from sqlalchemy import Column, Integer, String, Boolean, Float

class Publishing(Enum):

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


class AppUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=False)
    tg_id = Column(Integer, nullable=False, unique=True)
    phone_number = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    is_lessor = Column(Boolean, nullable=True)
    city_id = Column(Integer, nullable=True)
    score = Column(Float, default=0)



