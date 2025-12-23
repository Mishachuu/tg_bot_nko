from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from app.bot.state import SearchState
from app.db.session import AsyncSessionLocal
from app.bot.helpers import get_category_name
from datetime import datetime
from typing import Any


class SearchHandler:
    def __init__(self, category_service, equipment_service, equipment_photo_service, user_service, booking_service, formatter):
        self.category_service = category_service
        self.equipment_service = equipment_service
        self.equipment_photo_service = equipment_photo_service
        self.user_service = user_service
        self.booking_service = booking_service
        self.formatter = formatter

    async def start_search_flow(self, update, user_states: dict, user_id: int):
        user_states[user_id] = {
            "state": "asking_location",
            "data": SearchState(),
        }
        location_keyboard = [[{"text": "📍 Отправить локацию", "request_location": True}]]
        await update.message.reply_text(
            "📍 Для поиска оборудования отправьте вашу локацию:",
            reply_markup=ReplyKeyboardMarkup([["📍 Отправить локацию"]], resize_keyboard=True),
        )

