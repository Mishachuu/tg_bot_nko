from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from app.services.user_service import UserService # можно удалить но 
from app.db.session import AsyncSessionLocal

class NKOBot:
    """
    Основной класс бота для управления оборудованием.
    Простая и понятная структура для легкого расширения.
    """
    
    # Константы для состояний регистрации
    REGISTRATION_STATES = {
        'WAITING_FOR_NAME': 'waiting_for_name',
        'WAITING_FOR_CITY': 'waiting_for_city', 
        'WAITING_FOR_PHONE': 'waiting_for_phone',
        'WAITING_FOR_EMAIL': 'waiting_for_email'
    }

    def __init__(self, equipment_service, user_service: UserService):
        """
        Инициализация бота.
        
        Args:
            equipment_service: Сервис для работы с оборудованием
            user_service: Сервис для работы с пользователями
        """
        self.equipment_service = equipment_service
        self.user_service = user_service
        self.user_states = {}  # Храним состояния пользователей

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start
        Проверяет регистрацию пользователя и начинает процесс при необходимости.
        """
        user = update.effective_user
        user_id = user.id
        
        # Проверяем, зарегистрирован ли пользователь
        async with AsyncSessionLocal() as session:
            is_registered = await self.user_service.check_user(session, user_id)
        
        if is_registered:
            await self._show_main_menu(update, "С возвращением! Выберите действие:")
        else:
            await self._start_registration(update, user)

    async def _start_registration(self, update: Update, user):
        """
        Начинает процесс регистрации нового пользователя.
        """
        self.user_states[user.id] = {
            'state': self.REGISTRATION_STATES['WAITING_FOR_NAME'],
            'data': {}
        }
        
        await update.message.reply_text(
            "👋 Добро пожаловать! Давайте зарегистрируем вас в системе.\n"
            "Пожалуйста, введите ваше имя:"
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Основной обработчик текстовых сообщений.
        Распределяет сообщения по соответствующим обработчикам.
        """
        user_id = update.effective_user.id
        message_text = update.message.text

        # Проверяем состояние пользователя
        if user_id in self.user_states:
            await self._handle_registration_flow(update, user_id, message_text)
        else:
            await self._handle_regular_message(update, message_text)

    async def _handle_registration_flow(self, update: Update, user_id: int, message_text: str):
        """
        Обрабатывает сообщения во время процесса регистрации.
        """
        user_state = self.user_states[user_id]
        current_state = user_state['state']
        user_data = user_state['data']

        if current_state == self.REGISTRATION_STATES['WAITING_FOR_NAME']:
            await self._process_name_input(update, user_id, message_text, user_data)
            
        elif current_state == self.REGISTRATION_STATES['WAITING_FOR_CITY']:
            await self._process_city_input(update, user_id, message_text, user_data)
            
        elif current_state == self.REGISTRATION_STATES['WAITING_FOR_PHONE']:
            await self._process_phone_input(update, user_id, message_text, user_data)
            
        elif current_state == self.REGISTRATION_STATES['WAITING_FOR_EMAIL']:
            await self._process_email_input(update, user_id, message_text, user_data)

    async def _process_name_input(self, update: Update, user_id: int, name: str, user_data: dict):
        """Обрабатывает ввод имени"""
        user_data['name'] = name
        self.user_states[user_id]['state'] = self.REGISTRATION_STATES['WAITING_FOR_CITY']
        
        await update.message.reply_text("🏙️ В каком городе вы находитесь?")

    async def _process_city_input(self, update: Update, user_id: int, city: str, user_data: dict):
        """Обрабатывает ввод города"""
        user_data['city'] = city
        self.user_states[user_id]['state'] = self.REGISTRATION_STATES['WAITING_FOR_PHONE']
        
        # Создаем кнопку для отправки телефона
        phone_keyboard = [[KeyboardButton("📱 Отправить мой телефон", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(phone_keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "📞 Какой у вас номер телефона?",
            reply_markup=reply_markup
        )

    async def _process_phone_input(self, update: Update, user_id: int, phone: str, user_data: dict):
        """Обрабатывает ввод телефона"""
        user_data['phone'] = phone
        self.user_states[user_id]['state'] = self.REGISTRATION_STATES['WAITING_FOR_EMAIL']
        
        await update.message.reply_text(
            "📧 Введите ваш email (или напишите 'пропустить', если не хотите указывать):",
            reply_markup=ReplyKeyboardMarkup.remove_keyboard()  # Убираем специальную клавиатуру
        )

    async def _process_email_input(self, update: Update, user_id: int, email: str, user_data: dict):
        """Обрабатывает ввод email и завершает регистрацию"""
        if email.lower() != 'пропустить':
            user_data['email'] = email
        else:
            user_data['email'] = None

        # Сохраняем пользователя в базу данных
        async with AsyncSessionLocal() as session:
            await self.user_service.create_user(
                session=session,
                tg_id=user_id,
                name=user_data['name'],
                city=user_data['city'],
                phone=user_data['phone'],
                email=user_data['email']
            )

        # Очищаем состояние пользователя
        del self.user_states[user_id]
        
        await self._show_main_menu(update, "✅ Регистрация завершена! Теперь вы можете пользоваться ботом.")

    async def _show_main_menu(self, update: Update, message: str):
        """
        Показывает главное меню пользователю.
        
        Args:
            update: Объект Update от Telegram
            message: Сообщение для показа над меню
        """
        menu_buttons = [
            ["📋 Каталог оборудования", "🔍 Поиск"],
            ["⭐ Избранное", "🛠️ Мои заявки"],
            ["ℹ️ Помощь", "👤 Профиль"]
        ]
        
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)

    async def _handle_regular_message(self, update: Update, message_text: str):
        """
        Обрабатывает обычные сообщения (после регистрации).
        Здесь можно добавить логику для работы с основными функциями бота.
        """
        if message_text == "📋 Каталог оборудования":
            await self._show_equipment_catalog(update)
        elif message_text == "👤 Профиль":
            await self._show_user_profile(update)
        elif message_text == "ℹ️ Помощь":
            await self._show_help(update)
        else:
            await update.message.reply_text("Не понял вашу команду. Используйте кнопки меню.")

    async def _show_equipment_catalog(self, update: Update):
        """Показывает каталог оборудования"""
        # Здесь будет логика показа каталога
        await update.message.reply_text("📋 Раздел каталога оборудования в разработке...")

    async def _show_user_profile(self, update: Update):
        """Показывает профиль пользователя"""
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
        """Показывает справку"""
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

    def get_handlers(self):
        """
        Возвращает список обработчиков для регистрации в диспетчере.
        Новые обработчики добавляются по аналогии.
        """
        return [
            CommandHandler('start', self.start),
            CommandHandler('help', self._show_help),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler),
            MessageHandler(filters.CONTACT, self._handle_contact_shared),
        ]

    async def _handle_contact_shared(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает отправку контакта пользователем.
        """
        user_id = update.effective_user.id
        
        if user_id in self.user_states:
            contact = update.message.contact
            phone_number = contact.phone_number
            
            # Продолжаем процесс регистрации с полученным номером
            user_state = self.user_states[user_id]
            user_data = user_state['data']
            
            await self._process_phone_input(update, user_id, phone_number, user_data)