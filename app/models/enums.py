from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELED = "canceled"
    
    @property
    def label(self) -> str:
        labels = {
            BookingStatus.PENDING: "Ожидает подтверждения",
            BookingStatus.ACCEPTED: "Подтверждено",
            BookingStatus.DECLINED: "Отклонено",
            BookingStatus.CANCELED: "Отменено",
        }
        return labels[self]
