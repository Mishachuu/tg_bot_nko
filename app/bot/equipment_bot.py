from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.services.equipment_service import EquipmentService
from app.services.category_service import CategoryService
from app.bot.equipment_card_formatter import EquipmentCardFormatter
from app.db.session import AsyncSessionLocal
from app.repositories.category_repository import CategoryRepository
from app.db.tables import category_table, equipment_table

class EquipmentBot:
    def __init__(self, equipment_service: EquipmentService):
        self.equipment_service = equipment_service
        self.formatter = EquipmentCardFormatter()
        self.users = {1: "Иван Петров", 2: "Анна Сидорова", 3: "Петр Иванов"}

        # Состояния и временный выбор пользователя:
        # user_id -> {"state": str, "selected_categories": set}
        self._user_state = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        main_keyboard = [["📦 Доступное оборудование"]]
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "👋 Добро пожаловать!\nВыберите действие:",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user_id = update.effective_user.id

        user_data = self._user_state.get(user_id, {"state": None, "selected_categories": set()})

        if text == "📦 Доступное оборудование":
            # Сбрасываем выбор и переходим в режим выбора категорий
            user_data["state"] = "choosing_categories"
            user_data["selected_categories"] = set()
            self._user_state[user_id] = user_data
            await self.ask_categories(update, context, user_data["selected_categories"])

        elif user_data["state"] == "choosing_categories":
            if text == "🔍 Найти":
                # Поиск по выбранным категориям
                if not user_data["selected_categories"]:
                    await update.message.reply_text("❗ Выберите хотя бы одну категорию перед поиском.")
                    return
                await self.show_equipment_by_categories(update, context, user_data["selected_categories"])
                # Завершаем выбор категорий
                self._user_state.pop(user_id, None)
            else:
                # Обработка выбора / отмены выбора категории
                await self.toggle_category_selection(update, context, text, user_data)
                # обновляем состояние
                self._user_state[user_id] = user_data
        else:
            await update.message.reply_text("🤔 Не понимаю команду. Используйте кнопки меню.")

    async def ask_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selected_categories: set):
        async with AsyncSessionLocal() as session:
            cat_repo = CategoryRepository(category_table)
            cat_service = CategoryService(cat_repo)
            categories = await cat_service.list_categories(session)

        if not categories:
            await update.message.reply_text("⚠️ В базе нет категорий.")
            return

        # Формируем клавиатуру с отметками выбранных категорий
        keyboard = []
        for c in categories:
            name = c["name"]
            if c["id"] in selected_categories:
                display_name = f"✅ {name}"
            else:
                display_name = name
            keyboard.append([display_name])

        # Добавляем кнопку "Найти"
        keyboard.append(["🔍 Найти"])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📂 Выберите категории (можно несколько):", reply_markup=reply_markup)

    async def toggle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, user_data: dict):
        # Убираем галочку из названия, если есть
        if text.startswith("✅ "):
            category_name = text[2:].strip()
        else:
            category_name = text.strip()

        async with AsyncSessionLocal() as session:
            cat_repo = CategoryRepository(category_table)
            cat_service = CategoryService(cat_repo)
            categories = await cat_service.list_categories(session)

        # Найдем категорию по имени
        category = next((c for c in categories if c["name"] == category_name), None)
        if not category:
            await update.message.reply_text("❌ Неизвестная категория. Попробуйте снова.")
            return

        cat_id = category["id"]
        if cat_id in user_data["selected_categories"]:
            user_data["selected_categories"].remove(cat_id)
        else:
            user_data["selected_categories"].add(cat_id)

        # Обновляем клавиатуру с новыми отметками
        await self.ask_categories(update, context, user_data["selected_categories"])

    async def show_equipment_by_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category_ids: set):
        async with AsyncSessionLocal() as session:
            all_equipment = []
            for cat_id in category_ids:
                eqs = await self.equipment_service.find_by_category(session, cat_id)
                all_equipment.extend(eqs)

        available_equipment = [
            eq for eq in all_equipment
            if eq.landlord_id != 1 and eq.status.value == "available"
        ]

        if not available_equipment:
            await update.message.reply_text("😔 Нет доступного оборудования по выбранным категориям.")
            return

        await update.message.reply_text(
            f"📦 Доступное оборудование по выбранным категориям ({len(available_equipment)} позиций):"
        )

        for equipment in available_equipment:
            card_text = self.formatter.create_equipment_card(
                equipment,
                self.users.get(equipment.landlord_id, "Неизвестно")
            )
            keyboard = self.formatter.create_interaction_keyboard(equipment.id)
            await update.message.reply_text(
                card_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )

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
            CallbackQueryHandler(self.handle_callback)
        ]
