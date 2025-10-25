import logging
import asyncio
from telegram.ext import Application
from app.setting import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота (работает внутри asyncio.run)"""

    from app.repositories.booking_repository import BookingRepository
    from app.services.booking_service import BookingService
    from app.repositories.equipment_repository import EquipmentRepository
    from app.services.equipment_service import EquipmentService
    from app.bot.equipment_bot import EquipmentBot
    from app.db.tables import equipment_table
    from app.db.tables import bookings_table

    booking_repo = BookingRepository(bookings_table)
    booking_service = BookingService(booking_repo)
    repo = EquipmentRepository(equipment_table)
    equipment_service = EquipmentService(repo, booking_service)
    bot = EquipmentBot(equipment_service)

    token = TOKEN
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
