import asyncio
from app.db.init_db import init_db
from app.db.tables import category_table, equipment_table
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.repositories.equipment_repository import EquipmentRepository
from app.services.equipment_service import EquipmentService
from app.seed.mockup import MOCK_EQUIPMENT, CATEGORIES
from app.db.session import AsyncSessionLocal

async def init_database():
    """Создаёт таблицы в БД."""
    print("🧱 Инициализация базы данных...")
    await init_db()
    print("✅ Таблицы созданы.")


async def seed_mockup_data():
    async with AsyncSessionLocal() as session:
        cat_repo = CategoryRepository(category_table)
        cat_service = CategoryService(cat_repo)
        eq_repo = EquipmentRepository(equipment_table)
        eq_service = EquipmentService(eq_repo)

        # 🔹 Сид категорий
        print("📂 Добавляем категории...")
        await cat_service.seed_categories(session, [c["name"] for c in CATEGORIES])

        # 🔹 Сид оборудования
        print("📦 Добавляем оборудование...")
        for eq in MOCK_EQUIPMENT:
            try:
                await eq_service.create_equipment(session, eq)
            except Exception as e:
                print("⚠️ Ошибка при добавлении:", e)
        print("✅ Мокап загружен.")


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
