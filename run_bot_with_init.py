import asyncio
import sys
import os
#from app.setting import MOCKUP_REQUIRED
import os
from dotenv import load_dotenv

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.cli.db_init import db_init_main
from app.cli.bot_main import main as bot_main


async def main():
    """Запускает инициализацию БД, затем бота"""
    load_dotenv()
    MOCKUP_REQUIRED = os.getenv('MOCKUP_REQUIRED')
    
    print("🚀 Запуск инициализации базы данных...")
    await db_init_main(MOCKUP_REQUIRED)
    print("🎯 Запуск телеграм бота...")
    await bot_main()

if __name__ == "__main__":
    asyncio.run(main())