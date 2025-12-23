from app.db.session import AsyncSessionLocal
from app.models.user_app import AppUser
from app.models.enums import BookingStatus
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class BookingHandler:
    def __init__(self, booking_service, equipment_service, user_service, notification_service):
        self.booking_service = booking_service
        self.equipment_service = equipment_service
        self.user_service = user_service
        self.notification_service = notification_service

    async def start_booking_dialog(self, update, user_states, user_id, equipment_id: int):
        user_states[user_id] = {"state": "booking_entering_date_from", "data": {"equipment_id": equipment_id}}
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        await update.callback_query.message.reply_text("📅 Введите дату начала аренды в формате ДД.ММ.ГГГГ:")

