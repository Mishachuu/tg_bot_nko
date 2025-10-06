import asyncio
from app.db.session import engine
from app.db.tables import metadata

async def init_db():
    async with engine.begin() as conn:
        # Создание всех таблиц, если их ещё нет
        await conn.run_sync(metadata.create_all)
    print("✅ Таблицы (metadata) созданы.")
