from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.services.equipment_photo_service import EquipmentPhotoService
from app.services.equipment_service import EquipmentService
from app.services.category_service import CategoryService
from app.bot.equipment_card_formatter import EquipmentCardFormatter
from app.db.session import AsyncSessionLocal
from app.repositories.category_repository import CategoryRepository
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
#from app.db.tables import category_table, equipment_photos_table
from datetime import datetime
import io
from telegram import InputFile
from app.bot.bot_state import BotState
from app.helpers.gis_helper import calculate_distance

class EquipmentBot:
    def __init__(self, equipment_service: EquipmentService):
        self.equipment_service = equipment_service
        self.formatter = EquipmentCardFormatter()
        self.users = {1: "Иван Петров", 2: "Анна Сидорова", 3: "Петр Иванов"}

        self._user_state = {}

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        main_keyboard = [["📦 Отфильтровать оборудование"], ["Показать всё оборудование"], ["Назад"]]
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите поиск:",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message = update.message
        text = message.text.strip() if message.text else ""
        user_data = self._user_state.setdefault(user_id, {
            "state": BotState.MAIN_MENU,
            "selected_categories": set(),
            "date_from": None,
            "date_to": None,
            "location": None,
            "radius_km": 30
        })

        state = user_data["state"]

        # --- Главное меню ---
        if state == BotState.MAIN_MENU:
            if text == "📦 Доступное оборудование":
                user_data["state"] = BotState.ASKING_LOCATION
                await self.ask_location(update)
            else:
                await update.message.reply_text("Выберите действие из меню.")
            return

        # --- Получение радиуса ---
        elif state == BotState.ASKING_RADIUS:
            try:
                if text:
                    radius = int(text)
                    if radius <= 0:
                        raise ValueError
                    user_data["radius_km"] = radius
                else:
                    user_data["radius_km"] = 30
            except ValueError:
                await update.message.reply_text("⚠️ Введите число километров, например 15.")
                return

            user_data["state"] = BotState.CHOOSING_CATEGORIES
            await self.ask_categories(update, context, user_data["selected_categories"])
            return

        # --- Выбор категорий ---
        elif state == BotState.CHOOSING_CATEGORIES:
            if text == "🔍 Найти":
                if not user_data["selected_categories"]:
                    await update.message.reply_text("❗ Выберите хотя бы одну категорию.")
                    return
                user_data["state"] = BotState.ENTERING_DATE_FROM
                await update.message.reply_text("Введите дату начала аренды (ГГГГ.ММ.ДД):")
            else:
                await self.toggle_category_selection(update, context, text, user_data)
            return

        # --- Ввод даты начала ---
        elif state == BotState.ENTERING_DATE_FROM:
            try:
                user_data["date_from"] = datetime.strptime(text, "%Y.%m.%d")
                user_data["state"] = BotState.ENTERING_DATE_TO
                await update.message.reply_text("Введите дату окончания аренды (ГГГГ.ММ.ДД):")
            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат. Введите дату как ГГГГ.ММ.ДД.")
            return

        # --- Ввод даты окончания ---
        elif state == BotState.ENTERING_DATE_TO:
            try:
                user_data["date_to"] = datetime.strptime(text, "%Y.%m.%d")
                if user_data["date_to"] < user_data["date_from"]:
                    await update.message.reply_text("⚠️ Дата окончания не может быть раньше даты начала.")
                    return
                await self.show_equipment_by_categories_and_date(update, context, user_data)
                user_data["state"] = BotState.MAIN_MENU
            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат даты. Введите дату снова.")
            return

        # --- Неизвестное состояние ---
        else:
            await update.message.reply_text("⚙️ Непонятное состояние, возвращаюсь в главное меню.")
            user_data["state"] = BotState.MAIN_MENU
            await self.start(update, context)

    async def ask_location(self, update: Update):
        keyboard = [[KeyboardButton("📍 Отправить локацию", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "📍 Пожалуйста, отправьте вашу локацию, чтобы показать доступное оборудование рядом с вами:",
            reply_markup=reply_markup
        )

    async def show_equipment_by_categories_and_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
        async with AsyncSessionLocal() as session:
            available_equipment = []
            
            # Проверяем, есть ли локация у пользователя
            user_location = user_data.get("location")
            radius_km = user_data.get("radius_km", 30)
            
            for cat_id in user_data["selected_categories"]:
                # Используем метод с учетом локации
                eqs = await self.equipment_service.find_available_by_category_date_and_location(
                    session,
                    cat_id,
                    user_data["date_from"],
                    user_data["date_to"],
                    user_location["lat"],
                    user_location["lon"],
                    radius_km
                )
                available_equipment.extend(eqs)

            photo_repo = EquipmentPhotoRepository(equipment_photos_table)
            photo_service = EquipmentPhotoService(photo_repo)

            if not available_equipment:
                location_info = ""
                if user_location:
                    location_info = f" в радиусе {radius_km} км от вашей локации"
                
                keyboard = ReplyKeyboardMarkup([["🔄 Выбрать категории и даты"]], resize_keyboard=True)
                await update.message.reply_text(
                    f"😔 Нет свободного оборудования на выбранные даты{location_info}.",
                    reply_markup=keyboard
                )
                return

            location_info = ""
            if user_location:
                location_info = f" в радиусе {radius_km} км от вас"
                
            await update.message.reply_text(f"📦 Доступное оборудование{location_info} ({len(available_equipment)} позиций):")

            for eq in available_equipment:
                photos = await photo_service.list_photos(session, eq.id)
                card_text = self.formatter.create_equipment_card(eq, self.users.get(eq.landlord_id, "Неизвестно"))
                
                # Добавьте информацию о расстоянии, если есть локация
                if user_location and hasattr(eq, 'latitude') and hasattr(eq, 'longitude'):
                    distance = calculate_distance(
                        user_location["lat"], user_location["lon"],
                        eq.latitude, eq.longitude
                    )
                    card_text += f"\n📍 Расстояние: {distance:.1f} км"
                
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

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает получение локации от пользователя"""
        user_id = update.effective_user.id
        user_data = self._user_state.setdefault(user_id, {
            "state": BotState.MAIN_MENU,
            "selected_categories": set(),
            "date_from": None,
            "date_to": None,
            "location": None,
            "radius_km": 30
        })
        
        state = user_data["state"]
        
        # Обрабатываем локацию только если мы ее ожидаем
        if state == BotState.ASKING_LOCATION:
            location = update.message.location
            user_data["location"] = {
                "lat": location.latitude,
                "lon": location.longitude
            }
            print(f"Получена локация: {user_data['location']}")
            
            user_data["state"] = BotState.ASKING_RADIUS
            await update.message.reply_text(
                "📏 Укажите радиус поиска в километрах (по умолчанию 30 км):"
            )
        else:
            # Если локация получена не в том состоянии, игнорируем
            await update.message.reply_text("📍 Сначала выберите 'Доступное оборудование' для отправки локации.")
    
    

    def get_handlers(self):
        return [
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            CallbackQueryHandler(self.handle_callback, pattern=r"^(book_|ask_)"),
            MessageHandler(filters.LOCATION, self.handle_location),
        ]


