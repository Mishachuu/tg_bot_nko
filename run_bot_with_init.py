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

from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.repositories.city_repository import CityRepository



async def main():
    """Запускает инициализацию БД, затем бота"""
    load_dotenv()
    MOCKUP_REQUIRED = os.getenv('MOCKUP_REQUIRED')
    booking_repo = BookingRepository()
    repo_equipment = EquipmentRepository()
    repo_user = UserRepository()
    repo_city = CityRepository()
    repo_category = CategoryRepository()
    print("🚀 Запуск инициализации базы данных...")
    await db_init_main(booking_repo, repo_equipment, repo_user, repo_city, repo_category, MOCKUP_REQUIRED)
    print("🎯 Запуск телеграм бота...")
    await bot_main(booking_repo, repo_equipment, repo_user, repo_city, repo_category)

if __name__ == "__main__":
    asyncio.run(main())