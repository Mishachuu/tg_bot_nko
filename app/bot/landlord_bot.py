from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.services.landlord_service import LandlordService
from app.services.equipment_service import EquipmentService
from app.services.category_service import CategoryService
from app.repositories.category_repository import CategoryRepository
from app.repositories.booking_repository import BookingRepository
from app.db.session import AsyncSessionLocal
from app.db.tables import category_table
from app.models.equipment import Equipment
from datetime import datetime
import io


class LandlordBot:
    def __init__(self, landlord_service: LandlordService, equipment_service: EquipmentService):
        self.landlord_service = landlord_service
        self.equipment_service = equipment_service
        self._user_state = {}

    # ---------- Главное меню ----------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            ["Профиль", "Мое оборудование"],
            ["Бронирования", "Добавить оборудование"],
            ["Настройки"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=reply_markup
        )

    # ---------- Обработчик всех сообщений ----------
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        user_id = update.effective_user.id

        user_state = self._user_state.get(user_id, {"state": None, "buffer": {}})
        self._user_state[user_id] = user_state

        if text == "Профиль":
            await self.show_profile(update, context, user_id)
            return

        if text == "Мое оборудование":
            await self.show_equipment(update, context, user_id)
            return

        if text == "Бронирования":
            await self.show_bookings(update, context, user_id)
            return

        if text == "Добавить оборудование":
            await self.start_add_equipment(update, context, user_id)
            return

        if text == "Настройки":
            await update.message.reply_text("Настройки пока не реализованы.")
            return

        # Состояние добавления оборудования
        state = user_state["state"]
        if state == "add_name":
            user_state["buffer"]["name"] = text
            user_state["state"] = "add_category"
            await self.ask_category(update)
            return
        elif state == "add_category":
            user_state["buffer"]["category_name"] = text
            user_state["state"] = "add_city"
            await update.message.reply_text("Введите ID города (например, 1 — Москва):")
            return
        elif state == "add_city":
            try:
                user_state["buffer"]["city_id"] = int(text)
                user_state["state"] = "add_quantity"
                await update.message.reply_text("Введите количество:")
            except ValueError:
                await update.message.reply_text("Введите число (ID города).")
            return
        elif state == "add_quantity":
            try:
                user_state["buffer"]["quantity"] = int(text)
                user_state["state"] = "add_description"
                await update.message.reply_text("Введите описание:")
            except ValueError:
                await update.message.reply_text("Введите число.")
            return
        elif state == "add_description":
            user_state["buffer"]["description"] = text
            user_state["state"] = None
            await self.finish_add_equipment(update, context, user_id)
            return

        await update.message.reply_text("Неизвестная команда. Используйте меню.")

    # ---------- Профиль ----------
    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        landlord = await self.landlord_service.get_landlord(user_id)
        if not landlord:
            await update.message.reply_text("Профиль не найден. Вы еще не зарегистрированы.")
            return

        text = (
            f"ID: {landlord.id}\n"
            f"Имя: {landlord.name}\n"
            f"Телефоны: {', '.join(landlord.phone_numbers)}\n"
            f"Email: {', '.join(landlord.emails)}\n"
            f"Рейтинг: {landlord.score}"
        )

        keyboard = [["Изменить имя", "Изменить контакты"], ["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(text, reply_markup=reply_markup)

    # ---------- Список оборудования ----------
    async def show_equipment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        async with AsyncSessionLocal() as session:
            equipment_list = await self.equipment_service.list_equipment(session)
            equipment_list = [eq for eq in equipment_list if eq.landlord_id == user_id]

        if not equipment_list:
            await update.message.reply_text("У вас пока нет добавленного оборудования.")
            return

        for eq in equipment_list:
            text = (
                f"ID: {eq.id}\n"
                f"Название: {eq.name}\n"
                f"Категория: {eq.category_id}\n"
                f"Количество: {eq.quantity}\n"
                f"Описание: {eq.description or 'нет'}\n"
                f"Статус: {eq.status}"
            )
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Изменить", callback_data=f"edit_{eq.id}"),
                    InlineKeyboardButton("Удалить", callback_data=f"delete_{eq.id}")
                ]
            ])
            await update.message.reply_text(text, reply_markup=keyboard)

    # ---------- Просмотр бронирований ----------
    async def show_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        async with AsyncSessionLocal() as session:
            repo = BookingRepository()
            bookings = await repo.get_by_landlord(session, user_id) if hasattr(repo, "get_by_landlord") else []

        if not bookings:
            await update.message.reply_text("Активных бронирований нет.")
            return

        for b in bookings:
            text = (
                f"Оборудование ID: {b['equipment_id']}\n"
                f"Период: {b['date_from'].strftime('%Y-%m-%d')} - {b['date_to'].strftime('%Y-%m-%d')}\n"
                f"Арендатор ID: {b['user_id']}"
            )
            await update.message.reply_text(text)

    # ---------- Добавление оборудования ----------
    async def start_add_equipment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        self._user_state[user_id] = {"state": "add_name", "buffer": {}}
        await update.message.reply_text("Введите название оборудования:")

    async def ask_category(self, update: Update):
        async with AsyncSessionLocal() as session:
            repo = CategoryRepository(category_table)
            service = CategoryService(repo)
            categories = await service.list_categories(session)
        if not categories:
            await update.message.reply_text("Нет доступных категорий.")
            return
        names = [c["name"] for c in categories]
        await update.message.reply_text("Введите категорию из списка: " + ", ".join(names))

    async def finish_add_equipment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        data = self._user_state[user_id]["buffer"]
        eq = Equipment(
            name=data["name"],
            city_id=data["city_id"],
            landlord_id=user_id,
            status="available",
            photo=None,
            category_id=None,
            is_approved=False,
            description=data["description"],
            quantity=data["quantity"],
            created_at=datetime.utcnow()
        )

        async with AsyncSessionLocal() as session:
            await self.equipment_service.create_equipment(session, eq)

        self._user_state.pop(user_id, None)
        await update.message.reply_text("Оборудование добавлено.")
        await self.start(update, context)

    # ---------- Обработка inline-кнопок ----------
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data

        if data.startswith("edit_"):
            eq_id = int(data.split("_")[1])
            await query.edit_message_text(f"Изменение оборудования ID {eq_id} пока не реализовано.")
        elif data.startswith("delete_"):
            eq_id = int(data.split("_")[1])
            async with AsyncSessionLocal() as session:
                await self.equipment_service.delete_equipment(session, eq_id)
            await query.edit_message_text(f"Оборудование ID {eq_id} удалено.")

    # ---------- Регистрация обработчиков ----------
    def get_handlers(self):
        return [
            CommandHandler("start_landlord", self.start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            CallbackQueryHandler(self.handle_callback, pattern=r"^(edit_|delete_)"),
        ]
