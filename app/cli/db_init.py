import asyncio
from sqlalchemy import text
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.services.set_mockup_service import SetMockupService

# Надёжно ждём готовности Postgres
async def wait_for_db(max_attempts: int = 30, delay_sec: float = 1.0):
    attempt = 1
    while True:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ Соединение с БД установлено.")
            return
        except Exception as e:
            if attempt >= max_attempts:
                print(f"❌ БД так и не поднялась: {e}")
                raise
            print(f"⏳ БД ещё не готова (попытка {attempt}/{max_attempts}): {e}")
            await asyncio.sleep(delay_sec)
            attempt += 1

async def init_database():
    """Создаёт таблицы в БД."""
    print("🧱 Инициализация базы данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы (metadata) созданы.")

async def seed_mockup_data(booking_repo, repo_equipment, repo_user, repo_city, repo_category):
    service = SetMockupService(repo_equipment, booking_repo, repo_category, repo_user, repo_city)
    async with AsyncSessionLocal() as session:
        await service.create_users(session)
        await service.create_categories(session)
        await service.create_city(session)
        await service.create_equipments(session)
        await service.create_booking(session)
        # await service.create_photos(session)

async def db_init_main(booking_repo, repo_equipment, repo_user, repo_city, repo_category, seed: bool = False):
    print("🚀 Запуск инициализации базы данных...")
    # 1) ждём готовности Postgres
    await wait_for_db()
    # 2) создаём таблицы
    await init_database()
    # 3) при необходимости — сидим мок-данные
    if seed in (True, "True", "true", "1"):  # т.к. из .env приходит строка
        await seed_mockup_data(booking_repo, repo_equipment, repo_user, repo_city, repo_category)

if __name__ == "__main__":
    # для ручного запуска можно добавить заглушки/моки репоз
    pass