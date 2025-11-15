from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.db.base import Base
from app.models.booking_status import BookingStatus
from sqlalchemy import ForeignKey, Integer, Enum as SqlEnum


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date_from: Mapped[datetime] = mapped_column(nullable=False)
    date_to: Mapped[datetime] = mapped_column(nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus, name="booking_status_enum"), 
        nullable=False, 
        default=BookingStatus.PENDING
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "user_id": self.user_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "status": self.status.value,
            "quantity": self.quantity,
        }