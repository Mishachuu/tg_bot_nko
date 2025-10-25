# app/bot_main.py
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
    """Основная функция запуска бота"""

    from app.repositories.booking_repository import BookingRepository
    from app.services.booking_service import BookingService
    from app.repositories.equipment_repository import EquipmentRepository
    from app.services.equipment_service import EquipmentService
    from app.bot.equipment_bot import EquipmentBot
    from app.bot.landlord_bot import LandlordBot
    from app.services.landlord_service import LandlordService
    from app.db.tables import equipment_table, bookings_table

    booking_repo = BookingRepository(bookings_table)
    booking_service = BookingService(booking_repo)
    repo = EquipmentRepository(equipment_table)
    equipment_service = EquipmentService(repo, booking_service)
    landlord_service = LandlordService()

    equipment_bot = EquipmentBot(equipment_service)
    landlord_bot = LandlordBot(landlord_service, equipment_service)

    token = TOKEN
    if not token:
        logger.error("Не найден TOKEN бота.")
        return

    application = Application.builder().token(token).build()

    # Регистрируем обработчики обоих ботов
    for handler in equipment_bot.get_handlers():
        application.add_handler(handler)
    for handler in landlord_bot.get_handlers():
        application.add_handler(handler)

    print("Бот запущен. Для остановки — Ctrl+C")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("\nОстановка бота...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
