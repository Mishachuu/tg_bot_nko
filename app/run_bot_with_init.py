import asyncio
import sys
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
from app.repositories.review_repository import ReviewRepository
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository

async def main():
    """Запускает инициализацию БД, затем бота"""
    load_dotenv()
    MOCKUP_REQUIRED = os.getenv('MOCKUP_REQUIRED')
    
    # Создаем репозитории (без передачи таблиц, т.к. репозитории работают с ORM моделями)
    booking_repo = BookingRepository()
    repo_equipment = EquipmentRepository()
    repo_user = UserRepository()
    repo_category = CategoryRepository()
    repo_review = ReviewRepository()
    equipment_photo_repo = EquipmentPhotoRepository()
    
    print("🚀 Запуск инициализации базы данных...")
    await db_init_main(booking_repo, repo_equipment, repo_user, repo_category, MOCKUP_REQUIRED)
    print("🎯 Запуск телеграм бота...")
    
    # Передаем все репозитории в bot_main
    await bot_main(booking_repo, repo_equipment, repo_user, repo_category, repo_review, equipment_photo_repo)

if __name__ == "__main__":
    asyncio.run(main())