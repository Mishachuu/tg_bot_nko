from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.db.base import Base

class EquipmentPhoto(Base):
    __tablename__ = "equipment_photos"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[bytes] = mapped_column(nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "filename": self.filename,
            "content": self.content
        }