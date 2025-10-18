import asyncio

from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal
from app.repositories.equipment_repository import EquipmentRepository
from app.services.equipment_service import EquipmentService
from app.seed.mockup import MOCK_EQUIPMENT

async def ensure_db_and_seed():
    await init_db()

    async with AsyncSessionLocal() as session:
        from app.db.tables import equipment_table
        repo = EquipmentRepository(equipment_table)
        service = EquipmentService(repo)

        print("Загружаем мокап в базу...")
        for eq in MOCK_EQUIPMENT:
            try:
                await service.create_equipment(session, eq)
            except Exception as e:
                print("Ошибка при seed:", e)
        print("✅ Seed завершён.")

async def list_equipment():
    from app.db.tables import equipment_table
    async with AsyncSessionLocal() as session:
        repo = EquipmentRepository(equipment_table)
        service = EquipmentService(repo)
        equipment_list = await service.list_equipment(session)
        if not equipment_list:
            print("База пуста.")
        else:
            for eq in equipment_list:
                print(f"[{eq.id}] {eq.name} — {eq.status} — {eq.quantity} шт.")

async def cli_main():
    await asyncio.sleep(3)

    await ensure_db_and_seed()

    await list_equipment()

if __name__ == "__main__":
    asyncio.run(cli_main())