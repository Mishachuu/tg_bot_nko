import asyncio
import asyncpg
from config import setting

async def check_db_connection():
    try:
        # Прямая проверка подключения с asyncpg
        conn = await asyncpg.connect(setting.DATABASE_URL_asyncpg.replace('+asyncpg', ''))
        print("✅ Подключение к базе данных успешно")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

async def main():
    await check_db_connection()
    
if __name__ == "__main__":
    asyncio.run(main())