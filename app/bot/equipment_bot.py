from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.services.equipment_photo_service import EquipmentPhotoService
from app.services.equipment_service import EquipmentService
from app.services.category_service import CategoryService
from app.bot.equipment_card_formatter import EquipmentCardFormatter
from app.db.session import AsyncSessionLocal
from app.repositories.category_repository import CategoryRepository
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
from app.db.tables import category_table, equipment_table, equipment_photos_table
from datetime import datetime
from app.services.booking_service import BookingService
from app.repositories.booking_repository import BookingRepository
from app.db.tables import bookings_table
from datetime import timedelta
import io
from telegram import InputFile


class EquipmentBot:
    def __init__(self, equipment_service: EquipmentService):
        self.equipment_service = equipment_service
        self.formatter = EquipmentCardFormatter()
        self.users = {1: "Иван Петров", 2: "Анна Сидорова", 3: "Петр Иванов"}

        self._user_state = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        main_keyboard = [["📦 Доступное оборудование"]]
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "👋 Добро пожаловать!\nВыберите действие:",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        user_id = update.effective_user.id

        user_data = self._user_state.get(user_id, {
            "state": None,
            "selected_categories": set(),
            "date_from": None,
            "date_to": None,
        })

        if text in ["📦 Доступное оборудование", "🔄 Выбрать категории и даты"]:
            user_data["state"] = "choosing_categories"
            user_data["selected_categories"] = set()
            user_data["date_from"] = None
            user_data["date_to"] = None
            self._user_state[user_id] = user_data
            await self.ask_categories(update, context, user_data["selected_categories"])
            return

        if user_data["state"] == "choosing_categories":
            if text == "🔍 Найти":
                if not user_data["selected_categories"]:
                    await update.message.reply_text("❗ Выберите хотя бы одну категорию.")
                    return
                user_data["state"] = "entering_date_from"
                self._user_state[user_id] = user_data
                await update.message.reply_text("Введите дату начала аренды в формате ГГГГ.ММ.ДД (например, 2025.10.18):")
            else:
                await self.toggle_category_selection(update, context, text, user_data)
            return

        if user_data["state"] == "entering_date_from":
            try:
                user_data["date_from"] = datetime.strptime(text, "%Y.%m.%d")
                user_data["state"] = "entering_date_to"
                self._user_state[user_id] = user_data
                await update.message.reply_text("Введите дату окончания аренды в формате ГГГГ.ММ.ДД:")
            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат. Введите дату как ГГГГ.ММ.ДД.")
            return

        if user_data["state"] == "entering_date_to":
            try:
                user_data["date_to"] = datetime.strptime(text, "%Y.%m.%d")
                if user_data["date_to"] < user_data["date_from"]:
                    await update.message.reply_text("⚠️ Дата окончания не может быть раньше даты начала.")
                    return

                await self.show_equipment_by_categories_and_date(update, context, user_data)
                self._user_state.pop(user_id, None)  # Сброс состояния

            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат даты. Введите в формате ГГГГ.ММ.ДД.")
            return

        await update.message.reply_text("🤔 Не понимаю команду. Используйте кнопки меню.")

    async def show_equipment_by_categories_and_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
        async with AsyncSessionLocal() as session:
            available_equipment = []
            for cat_id in user_data["selected_categories"]:
                eqs = await self.equipment_service.find_available_by_category_and_date(
                    session,
                    cat_id,
                    user_data["date_from"],
                    user_data["date_to"]
                )
                available_equipment.extend(eqs)

            photo_repo = EquipmentPhotoRepository(equipment_photos_table)
            photo_service = EquipmentPhotoService(photo_repo)

            if not available_equipment:
                keyboard = ReplyKeyboardMarkup([["🔄 Выбрать категории и даты"]], resize_keyboard=True)
                await update.message.reply_text(
                    "😔 Нет свободного оборудования на выбранные даты.",
                    reply_markup=keyboard
                )
                return

            await update.message.reply_text(f"📦 Доступное оборудование ({len(available_equipment)} позиций):")

            for eq in available_equipment:
                photos = await photo_service.list_photos(session, eq.id)
                card_text = self.formatter.create_equipment_card(eq, self.users.get(eq.landlord_id, "Неизвестно"))
                keyboard = self.formatter.create_interaction_keyboard(eq.id)

                if photos:
                    first_photo = photos[0]["content"]
                    if isinstance(first_photo, memoryview):
                        first_photo = first_photo.tobytes()
                    await update.message.reply_photo(
                        photo=InputFile(io.BytesIO(first_photo), filename=f"eq_{eq.id}.jpg"),
                        caption=card_text,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_text(
                        card_text,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )

            restart_keyboard = ReplyKeyboardMarkup([["🔄 Выбрать категории и даты"]], resize_keyboard=True)
            await update.message.reply_text("Выберите действие", reply_markup=restart_keyboard)

    async def ask_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selected_categories: set):
        async with AsyncSessionLocal() as session:
            cat_repo = CategoryRepository(category_table)
            cat_service = CategoryService(cat_repo)
            categories = await cat_service.list_categories(session)

        if not categories:
            await update.message.reply_text("⚠️ В базе нет категорий.")
            return

        keyboard = []
        for c in categories:
            name = c["name"]
            if c["id"] in selected_categories:
                display_name = f"✅ {name}"
            else:
                display_name = name
            keyboard.append([display_name])

        keyboard.append(["🔍 Найти"])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📂 Выберите категории (можно несколько):", reply_markup=reply_markup)

    async def toggle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, user_data: dict):
        if text.startswith("✅ "):
            category_name = text[2:].strip()
        else:
            category_name = text.strip()

        async with AsyncSessionLocal() as session:
            cat_repo = CategoryRepository(category_table)
            cat_service = CategoryService(cat_repo)
            categories = await cat_service.list_categories(session)

        category = next((c for c in categories if c["name"] == category_name), None)
        if not category:
            await update.message.reply_text("❌ Неизвестная категория. Попробуйте снова.")
            return

        cat_id = category["id"]
        if cat_id in user_data["selected_categories"]:
            user_data["selected_categories"].remove(cat_id)
        else:
            user_data["selected_categories"].add(cat_id)

        await self.ask_categories(update, context, user_data["selected_categories"])

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data.startswith('book_'):
            equipment_id = int(callback_data.split('_')[1])
            await query.edit_message_text(
                f"📋 Бронирование оборудования ID: {equipment_id}\nФункция бронирования в разработке..."
            )
        elif callback_data.startswith('ask_'):
            equipment_id = int(callback_data.split('_')[1])
            await query.edit_message_text(
                f"💬 Вопрос по оборудованию ID: {equipment_id}\nФункция вопросов в разработке..."
            )

    def get_handlers(self):
        return [
            CommandHandler("start", self.start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            CallbackQueryHandler(self.handle_callback, pattern=r"^(book_|ask_)"),
        ]


