import asyncio
from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal
from app.repositories.equipment_repository import EquipmentRepository
from app.services.equipment_service import EquipmentService
from app.seed.mockup import MOCK_EQUIPMENT


async def init_database():
    """Создаёт таблицы в БД."""
    print("🧱 Инициализация базы данных...")
    await init_db()
    print("✅ Таблицы созданы.")


async def seed_mockup_data():
    """Загружает тестовые данные (мокап)."""
    from app.db.tables import equipment_table

    async with AsyncSessionLocal() as session:
        repo = EquipmentRepository(equipment_table)
        service = EquipmentService(repo)

        print("📦 Загружаем мокап данных...")
        for eq in MOCK_EQUIPMENT:
            try:
                await service.create_equipment(session, eq)
            except Exception as e:
                print(f"⚠️ Ошибка при добавлении оборудования {eq.name}: {e}")

        print("✅ Мокап успешно загружен.")


async def list_equipment():
    """Выводит содержимое таблицы оборудования."""
    from app.db.tables import equipment_table

    async with AsyncSessionLocal() as session:
        repo = EquipmentRepository(equipment_table)
        service = EquipmentService(repo)

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
