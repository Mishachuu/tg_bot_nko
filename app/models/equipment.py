from __future__ import annotations
from enum import StrEnum
from dataclasses import dataclass, asdict
from datetime import datetime

class RentalStatus(StrEnum):
    AVAILABLE = "available"
    BOOKED = "booked"
    IN_USE = "in_use"
    RETURNED = "returned"

@dataclass(slots=True)
class Equipment:
    """
    Класс оборудование
 
    attributes
    ----------
    id : int | None
        ID оборудования (Primary Key)
    name : str | None
        Название
    city_id: int | None
        Связный объект город в котором находится оборудование
    landlord_id: int | None
        ID арендодателя (связь с таблицей пользователей)
    status: RentalStatus
        Статус(available, booked, in_use, returned)
    photo: str | bytes | None
        str - либо URL либо file_id
        bytes - само изображение в бинарном формате
    category_id: int | None
        Связная таблица категория (звук, свет, мебель)
    is_approved: bool
        Подтверждено ли администратором (по умолчанию False)
    description : str | None
        Описание
    quantity: int 
        Кол-во
    created_at: datetime
        Дата создания
    """
    id: int | None = None
    name: str | None = None
    city_id: int | None = None
    landlord_id: int | None = None
    status: RentalStatus = RentalStatus.AVAILABLE
    photo: str | bytes | None = None

    category_id: int | None = None
    is_approved: bool = False
    description: str | None = None
    quantity: int = 1
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        # НЕ преобразуем created_at в строку, оставляем как datetime
        return d
