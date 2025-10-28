import logging
import asyncio
from telegram.ext import Application

from app.repositories.booking_repository import BookingRepository
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.user_repository import UserRepository

from app.services.booking_service import BookingService
from app.services.equipment_service import EquipmentService
from app.services.user_service import UserService
from app.bot.NKO_bot_2 import NKOBot
from app.db.tables import equipment_table
from app.db.tables import bookings_table
#from app.setting import TOKEN
import os
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота (работает внутри asyncio.run)"""

    booking_repo = BookingRepository(bookings_table)
    booking_service = BookingService(booking_repo)

    repo_equipment = EquipmentRepository()
    equipment_service = EquipmentService(repo_equipment, booking_service)

    repo_user =  UserRepository()
    user_service = UserService(repo_user)
    bot = NKOBot(equipment_service, user_service)

    load_dotenv("app/.env")
    token = os.getenv('TOKEN')
    if not token:
        logger.error("❌ Не найден TOKEN бота.")
        return

    application = Application.builder().token(token).build()

    # Регистрируем обработчики
    for handler in bot.get_handlers():
        application.add_handler(handler)

    print("🤖 Бот запускается...")
    print("⏹️  Для остановки нажмите Ctrl+C")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        await asyncio.Event().wait()  # просто "ждём вечно" пока не Ctrl+C
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Остановка бота...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
