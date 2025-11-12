
import logging
from telegram.ext import Application

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, application: Application):
        self.application = application
    
    async def notify_user(self, tg_id: int, message: str) -> bool:
        """Отправить уведомление пользователю через бота"""
        try:
            await self.application.bot.send_message(
                chat_id=tg_id,
                text=message
            )
            logger.info(f"✅ Уведомление отправлено пользователю {tg_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке уведомления пользователю {tg_id}: {e}")
            return False
