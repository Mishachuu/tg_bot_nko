from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from app.services.user_service import UserService  # можно удалить но
from app.db.session import AsyncSessionLocal


class NKOBot:
    """
    Основной класс бота для управления оборудованием.
    Чистая и модульная структура для удобного чтения и расширения.
    """
    # Константы состояний регистрации
    REGISTRATION_STATES = {
        "WAITING_FOR_NAME": "waiting_for_name",
        "WAITING_FOR_CITY": "waiting_for_city",
        "WAITING_FOR_PHONE": "waiting_for_phone",
        "WAITING_FOR_EMAIL": "waiting_for_email",
    }

    # Тексты кнопок (централизовано чтобы потом было проще править)
    BTN_SEND_CONTACT = "📱 Отправить мой телефон"
    BTN_SKIP = "Пропустить"

    def __init__(self, equipment_service, user_service: UserService):
        self.equipment_service = equipment_service
        self.user_service = user_service
        self.user_states: dict[int, dict] = {}  # временные состояния пользователей

    # ------------------------ Команды ------------------------
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /start — проверяет регистрацию и стартует её при необходимости."""
        user = update.effective_user
        user_id = user.id

        async with AsyncSessionLocal() as session:
            is_registered = await self.user_service.check_user(session, user_id)

        if is_registered:
            await self._show_main_menu(update, "С возвращением! Выберите действие:")
        else:
            await self._start_registration(update, user)

    async def _start_registration(self, update: Update, user):
        """Запускает регистрацию и просит имя пользователя."""
        self.user_states[user.id] = {"state": self.REGISTRATION_STATES["WAITING_FOR_NAME"], "data": {}}

        # Убираем любые клавиатуры и просим имя
        await update.message.reply_text(
            "👋 Добро пожаловать! Давайте зарегистрируем вас в системе.\n"
            "Пожалуйста, введите ваше имя:",
            reply_markup=ReplyKeyboardRemove(),
        )

    # ------------------------ Обработка сообщений ------------------------
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главный обработчик текстовых сообщений: маршрутизирует по состоянию пользователя."""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()

        if user_id in self.user_states:
            await self._handle_registration_flow(update, user_id, message_text)
        else:
            await self._handle_regular_message(update, message_text)

    async def _handle_registration_flow(self, update: Update, user_id: int, message_text: str):
        """Роутер для шагов регистрации."""
        user_state = self.user_states[user_id]
        current_state = user_state["state"]
        user_data = user_state["data"]

        if current_state == self.REGISTRATION_STATES["WAITING_FOR_NAME"]:
            await self._process_name_input(update, user_id, message_text, user_data)

        elif current_state == self.REGISTRATION_STATES["WAITING_FOR_CITY"]:
            await self._process_city_input(update, user_id, message_text, user_data)

        elif current_state == self.REGISTRATION_STATES["WAITING_FOR_PHONE"]:
            await self._process_phone_input(update, user_id, message_text, user_data)

        elif current_state == self.REGISTRATION_STATES["WAITING_FOR_EMAIL"]:
            await self._process_email_input(update, user_id, message_text, user_data)

    # ------------------------ Шаги регистрации ------------------------
    async def _process_name_input(self, update: Update, user_id: int, name: str, user_data: dict):
        """Сохраняет имя и спрашивает город."""
        user_data["name"] = name
        self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_CITY"]

        await update.message.reply_text("🏙️ В каком городе вы находитесь?")

    async def _process_city_input(self, update: Update, user_id: int, city: str, user_data: dict):
        """Сохраняет город и предлагает ввести номер телефона — с кнопками отправки контакта или пропуска."""
        user_data["city"] = city
        self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_PHONE"]

        # Клавиатура с возможностью отправить контакт и кнопкой пропустить
        phone_keyboard = [
            [KeyboardButton(self.BTN_SEND_CONTACT, request_contact=True)],
            [KeyboardButton(self.BTN_SKIP)],
        ]
        reply_markup = ReplyKeyboardMarkup(phone_keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            "📞 Пожалуйста, отправьте ваш номер телефона или нажмите 'Пропустить', если вы не хотите указывать:",
            reply_markup=reply_markup,
        )

    async def _process_phone_input(self, update: Update, user_id: int, phone: str, user_data: dict):
        """Обрабатывает телефон: принимает либо реальный номер, либо нажатие 'Пропустить'."""
        # Стандартный текст для 'пропустить' — сравниваем регистронезависимо
        if phone is None or (isinstance(phone, str) and phone.lower() == self.BTN_SKIP.lower()):
            user_data["phone"] = None
        else:
            user_data["phone"] = phone

        # Переходим к запросу email — убираем пользовательскую клавиатуру
        self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_EMAIL"]

        await update.message.reply_text(
            "📧 Введите ваш email (или нажмите 'Пропустить'):",
            reply_markup=ReplyKeyboardMarkup([[self.BTN_SKIP]], resize_keyboard=True, one_time_keyboard=True),
        )

    async def _process_email_input(self, update: Update, user_id: int, email: str, user_data: dict):
        """Обрабатывает email и завершает регистрацию, сохраняет пользователя в БД."""
        if email and email.strip().lower() != self.BTN_SKIP.lower():
            user_data["email"] = email.strip()
        else:
            user_data["email"] = None

        # Сохраняем в базу
        async with AsyncSessionLocal() as session:
            await self.user_service.create_user(
                session=session,
                tg_id=user_id,
                name=user_data.get("name"),
                city_id=1,#city_id=user_data.get("city"),
                phone_number=user_data.get("phone"),
                email=user_data.get("email"),
            )

        # Убираем состояние и показываем главное меню — клавиатуру сбрасываем
        del self.user_states[user_id]
        await self._show_main_menu(update, "✅ Регистрация завершена! Теперь вы можете пользоваться ботом.")

    # ------------------------ UI: главное меню и прочее ------------------------
    async def _show_main_menu(self, update: Update, message: str):
        menu_buttons = [
            ["🛠️ Моё оборудование", "🔍 Поиск"],
            ["➕ Добавить оборудование", "📋 Моя бронь"],
            ["ℹ️ Помощь", "👤 Профиль"],
        ]
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)

        # Используем ReplyKeyboardRemove перед отправкой, чтобы убрать временные клавиатуры, если они остались
        await update.message.reply_text(message, reply_markup=reply_markup)

    async def _handle_regular_message(self, update: Update, message_text: str):
        """Обработчик обычных команд после регистрации."""
        if message_text == "📋 Каталог оборудования":
            await self._show_equipment_catalog(update)
        elif message_text == "👤 Профиль":
            await self._show_user_profile(update)
        elif message_text == "ℹ️ Помощь":
            await self._show_help(update)
        else:
            await update.message.reply_text("Не понял вашу команду. Используйте кнопки меню.")

    async def _show_equipment_catalog(self, update: Update):
        await update.message.reply_text("📋 Раздел каталога оборудования в разработке...")

    async def _show_user_profile(self, update: Update):
        user_id = update.effective_user.id
        async with AsyncSessionLocal() as session:
            user_profile = await self.user_service.get_user_profile(session, user_id)

        profile_text = (
            f"👤 Ваш профиль:\n"
            f"Имя: {user_profile['name']}\n"
            f"Город: {user_profile['city']}\n"
            f"Телефон: {user_profile['phone']}\n"
            f"Email: {user_profile['email'] or 'не указан'}"
        )
        await update.message.reply_text(profile_text)

    async def _show_help(self, update: Update):
        help_text = (
            "🤖 Помощь по боту:\n\n"
            "• 📋 Каталог - просмотр всего оборудования\n"
            "• 🔍 Поиск - поиск по каталогу\n"
            "• ⭐ Избранное - ваше избранное оборудование\n"
            "• 🛠️ Мои заявки - история ваших заявок\n"
            "• 👤 Профиль - ваши данные\n\n"
            "Для начала работы выберите 'Каталог оборудования'"
        )
        await update.message.reply_text(help_text)

    # ------------------------ Обработчики для диспетчера ------------------------
    def get_handlers(self):
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self._show_help),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler),
            MessageHandler(filters.CONTACT, self._handle_contact_shared),
        ]

    # ------------------------ Контакт (кнопка отправки контакта) ------------------------
    async def _handle_contact_shared(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка события: пользователь поделился контактом через клавиатуру."""
        user_id = update.effective_user.id
        contact = update.message.contact
        phone_number = contact.phone_number if contact else None

        if user_id in self.user_states:
            user_state = self.user_states[user_id]
            user_data = user_state["data"]
            # Передаём номер в общий обработчик телефона
            await self._process_phone_input(update, user_id, phone_number, user_data)
