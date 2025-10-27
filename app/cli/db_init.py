import asyncio
from app.db.tables import category_table, equipment_table, bookings_table, equipment_photos_table
from app.repositories.booking_repository import BookingRepository
from app.services.booking_service import BookingService
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.repositories.equipment_repository import EquipmentRepository
from app.services.equipment_service import EquipmentService
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
from app.services.equipment_photo_service import EquipmentPhotoService
from app.seed.mockup import MOCK_EQUIPMENT, CATEGORIES, MOCK_BOOKINGS, MOCK_EQUIPMENT_PHOTOS
from app.db.session import AsyncSessionLocal

import asyncio
from app.db.session import engine
from app.db.tables import metadata



async def init_database():
    """Создаёт таблицы в БД."""
    print("🧱 Инициализация базы данных...")
    async with engine.begin() as conn:
        # Создание всех таблиц, если их ещё нет
        await conn.run_sync(metadata.create_all)
    print("✅ Таблицы (metadata) созданы.")


async def seed_mockup_data():
    async with AsyncSessionLocal() as session:

        booking_repo = BookingRepository(bookings_table)
        booking_service = BookingService(booking_repo)
        cat_repo = CategoryRepository(category_table)
        cat_service = CategoryService(cat_repo)
        eq_repo = EquipmentRepository(equipment_table)
        eq_service = EquipmentService(eq_repo, booking_service)

        print("📂 Добавляем категории...")
        await cat_service.seed_categories(session, [c["name"] for c in CATEGORIES])
        print("💾 Сохраняем изменения...")
        await session.commit()


        print("📦 Добавляем оборудование...")
        for eq in MOCK_EQUIPMENT:
            try:
                await eq_service.create_equipment(session, eq)
            except Exception as e:
                print("⚠️ Ошибка при добавлении оборудования:", e)

        print("💾 Сохраняем изменения...")
        await session.commit()

        print("📅 Добавляем бронирования...")
        for booking in MOCK_BOOKINGS:
            try:
                await booking_service.create_booking(
                    session,
                    equipment_id=booking["equipment_id"],
                    user_id=booking["user_id"],
                    date_from=booking["date_from"],
                    date_to=booking["date_to"],
                )
            except Exception as e:
                print(f"⚠️ Ошибка при добавлении бронирования {booking['id']}: {e}")

        print("💾 Сохраняем изменения...")
        await session.commit()

        print("🖼 Добавляем фото оборудования...")
        photo_repo = EquipmentPhotoRepository(equipment_photos_table)
        photo_service = EquipmentPhotoService(photo_repo)

        for photo in MOCK_EQUIPMENT_PHOTOS:
            try:
                await photo_service.add_photo(
                    session,
                    equipment_id=photo["equipment_id"],
                    filename=photo["filename"],
                    content=photo["content"],
                )
            except Exception as e:
                print(f"⚠️ Ошибка при добавлении фото: {e}")

        print("✅ Мокап загружен (категории, оборудование, бронирования).")


async def list_equipment():
    """Выводит содержимое таблицы оборудования."""
    from app.db.tables import equipment_table

    async with AsyncSessionLocal() as session:
        booking_repo = BookingRepository(bookings_table)
        booking_service = BookingService(booking_repo)
        repo = EquipmentRepository(equipment_table)
        service = EquipmentService(repo, booking_service)

        equipment_list = await service.list_equipment(session)
        if not equipment_list:
            print("ℹ️ База пуста.")
        else:
            print("📋 Список оборудования:")
            for eq in equipment_list:
                print(f"[{eq.id}] {eq.name} — {eq.status.value} — {eq.quantity} шт.")


async def db_init_main(seed: bool = True):
    """Главная точка входа для инициализации БД и (опционально) загрузки мокапа."""
    await asyncio.sleep(3)  # подождать, пока контейнер Postgres поднимется
    await init_database()

    if seed:
        await seed_mockup_data()

    await list_equipment()


if __name__ == "__main__":
    asyncio.run(db_init_main())
