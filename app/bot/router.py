from telegram import Update
from telegram.ext import ContextTypes
from .main_bot import MainBot

class BotRouter:
    def __init__(self, user_service, equipment_service, booking_service, review_service, category_service):
        self.main_bot = MainBot(
            user_service, equipment_service, booking_service, review_service, category_service
        )

    def get_handlers(self):
        return self.main_bot.get_handlers()