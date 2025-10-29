import asyncio
#from app.repositories.booking_repository import BookingRepository
#from app.services.booking_service import BookingService
#from app.repositories.category_repository import CategoryRepository
#from app.services.category_service import CategoryService
#from app.repositories.equipment_repository import EquipmentRepository
#from app.services.equipment_service import EquipmentService
#from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
#from app.services.equipment_photo_service import EquipmentPhotoService
from app.seed.mockup import MOCK_EQUIPMENT, CATEGORIES, MOCK_BOOKINGS, MOCK_EQUIPMENT_PHOTOS
from app.db.session import AsyncSessionLocal

import asyncio
from app.db.session import engine
from app.db.base import Base



async def init_database():
    """Создаёт таблицы в БД."""
    print("🧱 Инициализация базы данных...")
    async with engine.begin() as conn:
        # Создание всех таблиц, если их ещё нет
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы (metadata) созданы.")


async def seed_mockup_data():
    pass


async def db_init_main(seed: bool = True):
    """Главная точка входа для инициализации БД и (опционально) загрузки мокапа."""
    await asyncio.sleep(3)  # подождать, пока контейнер Postgres поднимется
    await init_database()

    if seed:
        await seed_mockup_data()


if __name__ == "__main__":
    asyncio.run(db_init_main())
