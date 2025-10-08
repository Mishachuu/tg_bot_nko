import os
import logging
from telegram.ext import Application
from app.setting import TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    
    # Инициализация сервисов
    from app.repositories.equipment_repository import EquipmentRepository
    from app.services.equipment_service import EquipmentService
    from app.bot.equipment_bot import EquipmentBot
    
    # Создаем и настраиваем сервисы
    equipment_repository = EquipmentRepository()
    equipment_service = EquipmentService(equipment_repository)
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
    
    # Запускаем бота (блокирующий вызов)
    application.run_polling()

if __name__ == "__main__":
    main()