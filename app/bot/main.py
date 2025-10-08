# main.py - точка входа бота
import os
import logging
import asyncio
from app.services.equipment_service import EquipmentService 
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.bot.equipment_bot import EquipmentBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Получаем токен бота из переменных окружения
    BOT_TOKEN = '8412664239:AAFfNwq7-IFDfuhHjersJcOvpFzOfRnnmVI'
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    try:
        # Создаем приложение бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Импортируем здесь чтобы избежать циклических импортов
        from app.bot.equipment_bot import EquipmentBot
        from app.services.equipment_service import EquipmentService
        
        # Инициализация бота
        equipment_service = EquipmentService(None)
        bot = EquipmentBot(equipment_service)
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        application.add_handler(CallbackQueryHandler(bot.handle_callback))
        
        # Запускаем бота
        logger.info("Bot is starting...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())