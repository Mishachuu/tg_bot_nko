import logging
import asyncio
from telegram.ext import Application
from dotenv import load_dotenv
import os

# Сервисы
from app.services.booking_service import BookingService
from app.services.equipment_service import EquipmentService
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.review_service import ReviewService
from app.services.equipment_photo_service import EquipmentPhotoService
from app.services.notification_service import NotificationService
# Новая модульная архитектура бота
from app.bot.router import BotRouter
from telegram.ext import Application
from dotenv import load_dotenv

load_dotenv("app/.env")
token = os.getenv('TOKEN')
# Создаем приложение
application = Application.builder().token(token).build()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main(booking_repo, repo_equipment, repo_user, repo_category, repo_review, equipment_photo_repo):
    """Основная функция запуска бота с новой модульной архитектурой"""
        # Загрузка токена бота
    notification_service = NotificationService(application)

    # Инициализация сервисов с переданными репозиториями
    booking_service = BookingService(booking_repo)
    equipment_service = EquipmentService(repo_equipment, booking_service)
    user_service = UserService(repo_user)
    category_service = CategoryService(repo_category)
    review_service = ReviewService(repo_review)
    equipment_photo_service = EquipmentPhotoService(equipment_photo_repo)

    # Создаем главный роутер вместо отдельных ботов
    bot_router = BotRouter(
        user_service=user_service,
        equipment_service=equipment_service,
        booking_service=booking_service,
        review_service=review_service,
        category_service=category_service,
        equipment_photo_service = equipment_photo_service
    )


    # Регистрируем ВСЕ обработчики через роутер
    for handler in bot_router.get_handlers():
        application.add_handler(handler)

    print("🤖 Бот запускается...")
    print("🏗️  Используется модульная архитектура")
    print("⏹️  Для остановки нажмите Ctrl+C")

    # Запускаем бота
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        await asyncio.Event().wait()  # ждем вечно пока не Ctrl+C
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Остановка бота...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


# Для возможности запуска напрямую (если нужно)
if __name__ == "__main__":
    # Создаем репозитории для прямого запуска
    from app.repositories.booking_repository import BookingRepository
    from app.repositories.equipment_repository import EquipmentRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.category_repository import CategoryRepository
    from app.repositories.review_repository import ReviewRepository
    
    booking_repo = BookingRepository()
    repo_equipment = EquipmentRepository()
    repo_user = UserRepository()
    repo_category = CategoryRepository()
    repo_review = ReviewRepository()
    
    asyncio.run(main(booking_repo, repo_equipment, repo_user, repo_category, repo_review))