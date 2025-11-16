from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.repositories.booking_repository import BookingRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.user_repository import UserRepository
from app.services.booking_service import BookingService
from app.services.category_service import CategoryService
from app.services.equipment_service import EquipmentService
from app.services.user_service import UserService
from app.services.equipment_photo_service import EquipmentPhotoService
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_booking_service() -> BookingService:
    repo = BookingRepository()
    return BookingService(repo)


def get_category_service() -> CategoryService:
    repo = CategoryRepository()
    return CategoryService(repo)


async def get_equipment_service() -> EquipmentService:
    equipment_repo = EquipmentRepository()
    booking_repo = BookingRepository()
    booking_service = BookingService(booking_repo)
    return EquipmentService(equipment_repo, booking_service)


def get_user_service() -> UserService:
    repo = UserRepository()
    return UserService(repo)

def get_equipment_photo_service():
    return EquipmentPhotoService(EquipmentPhotoRepository())