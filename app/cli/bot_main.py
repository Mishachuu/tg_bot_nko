import os
import logging
import asyncio
from telegram.ext import Application
from app.setting import TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Инициализация сервисов
    from app.repositories.equipment_repository import EquipmentRepository
    from app.services.equipment_service import EquipmentService
    from app.bot.equipment_bot import EquipmentBot
    from app.db.tables import equipment_table
    
    # Создаем и настраиваем сервисы
    repo = EquipmentRepository(equipment_table)
    equipment_service = EquipmentService(repo)
    bot = EquipmentBot(equipment_service)
    
    # Создаем приложение бота
    token = TOKEN
    if not token:
        return
    
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    for handler in bot.get_handlers():
        application.add_handler(handler)
    
    print("🤖 Бот запускается...")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())