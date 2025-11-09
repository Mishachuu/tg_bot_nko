from abc import ABC, abstractmethod
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.session import AsyncSessionLocal

class BaseBot(ABC):
    def __init__(self, user_service, equipment_service, booking_service, review_service):
        self.user_service = user_service
        self.equipment_service = equipment_service
        self.booking_service = booking_service
        self.review_service = review_service
        self.user_states = {}

    async def get_user_role(self, user_id: int) -> str:
        """Определяет роль пользователя"""
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)
            if not user:
                return "unregistered"
            return "lessor" if user.is_lessor else "lessee"

    async def show_main_menu(self, update: Update, user_id: int, message: str = ""):
        """Показывает главное меню в зависимости от роли"""
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)
            if not user:
                return
                
        if user.is_lessor:
            # Арендодатель: просмотр + управление оборудованием
            menu_buttons = [
                ["🔍 Найти оборудование"],
                ["➕ Добавить оборудование", "🛠️ Моё оборудование"],
                ["📋 Мои бронирования"]
            ]
        else:
            # Арендатор: только просмотр и бронирования
            menu_buttons = [
                ["🔍 Найти оборудование"],
                ["📋 Мои бронирования"]
            ]
            
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        await update.message.reply_text(message or "Выберите действие:", reply_markup=reply_markup)

    @abstractmethod
    def get_handlers(self):
        pass

    @abstractmethod
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass