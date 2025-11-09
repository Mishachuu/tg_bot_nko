from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AppUser(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    is_lessor: Mapped[bool] = mapped_column(default=False)
    score: Mapped[float] = mapped_column(default=0.0)  # заглушка, будет вычисляться из отзывов

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tg_id": self.tg_id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "is_lessor": self.is_lessor,
            "score": self.score,
        }