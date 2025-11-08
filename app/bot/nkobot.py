from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from app.services.user_service import UserService  # можно удалить но
from app.db.session import AsyncSessionLocal
from app.bot.equipment_bot import EquipmentBot
from app.bot.bot_state import BotState
from app.services.city_service import CityService
from app.models.equipment import Equipment
from app.models.user_app import AppUser
from datetime import datetime
from app.services.review_service import ReviewService
from app.repositories.review_repository import ReviewRepository

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
        "ADD_BOOK_EQUIPMENT_ID": "add_book_equipment_id",
        "ADD_BOOK_DATE_FROM": "add_book_date_from",
        "ADD_BOOK_DATE_TO": "add_book_date_to",
    }

    # Тексты кнопок (централизовано чтобы потом было проще править)
    BTN_SEND_CONTACT = "📱 Отправить мой телефон"
    BTN_SKIP = "Пропустить"

    def __init__(self, equipment_service, user_service: UserService, city_service:CityService):
        # Сепрвисы:
        self.equipment_service = equipment_service
        self.user_service = user_service
        self.city_service = city_service
        self.review_service = ReviewService(ReviewRepository())

        self.user_states: dict[int, dict] = {}  # временные состояния пользователей
        self.equipment_bot = EquipmentBot(equipment_service)

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
        message_text = (update.message.text or "").strip()

        if user_id in self.user_states:
            state = self.user_states[user_id]["state"]

            # --- регистрация ---
            if state in self.REGISTRATION_STATES.values():
                await self._handle_registration_flow(update, user_id, message_text)
                return

            # --- добавление оборудования ---
            if state.startswith("add_eq_"):
                await self._handle_equipment_flow(update, message_text)
                return

            # --- добавление брони ---
            if state.startswith("ADD_BOOK_"):
                await self._handle_booking_flow(update, user_id, message_text)
                return

            # --- добавление отзыва ---
            if state.startswith("review_"):
                await self._handle_review_flow(update, user_id, message_text)
                return

        # если нет активного состояния — обычная команда
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
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, update.effective_user.id)
        if(user.publish):
            menu_buttons = [
                ["➕ Добавить оборудование", "🛠️ Моё оборудование"],
                ["➕ Добавить бронь", "📋 Моя бронь"],
                ["🔍 Поиск", "👤 Профиль"],
                ["📝 Оставить отзыв"],
                ["ℹ️ Помощь"],
            ]
        elif(user.publish == False):
            menu_buttons = [
                ["🔍 Поиск", "📋 Моя бронь"],
                ["Отправить запрос на публикацию оборудования"],
                ["ℹ️ Помощь", "👤 Профиль"],
                ["📝 Оставить отзыв"],
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
        elif message_text == "🔍 Поиск":
            await self.handle_search(update)
        elif message_text == "📦 Отфильтровать оборудование":
            self.equipment_bot.user_data["state"] = BotState.ASKING_LOCATION
            await self.equipment_bot.ask_location(update)
        elif message_text == "📋 Моя бронь":
            await self._show_my_bookings(update)
        elif message_text == "📝 Оставить отзыв":
            await self._start_review_flow(update)
            
        elif message_text in ["➕ Добавить оборудование", "🛠️ Моё оборудование", "➕ Добавить бронь"]:
            async with AsyncSessionLocal() as session:
                user = await self.user_service.get_user_profile(session, update.effective_user.id)

            if not user or not user.publish:
                await update.message.reply_text(
                    "❌ У вас нет прав на публикацию оборудования.\n"
                    "Если вы хотите стать арендодателем, сделайте запрос на публикацию."
                )
                return

            if message_text == "➕ Добавить оборудование":
                await self._start_add_equipment_flow(update)
            elif message_text == "🛠️ Моё оборудование":
                await self._show_my_equipment(update)
            elif message_text == "➕ Добавить бронь":
                await self._start_add_booking_flow(update)
        elif message_text.lower().startswith("публикация "):
            parts = message_text.split()
            if len(parts) == 3:
                _, id_str, flag = parts
                try:
                    eq_id = int(id_str)
                    is_on = flag.lower() in ("on", "вкл", "да", "true", "1")
                except:
                    await update.message.reply_text("Формат: публикация <id> <on/off>")
                    return
                async with AsyncSessionLocal() as session:
                    updated = await self.equipment_service.set_publish(session, eq_id, is_on)
                if updated:
                    await update.message.reply_text(f"Готово: {updated.name} — {updated.display_status}")
                else:
                    await update.message.reply_text("Не нашёл оборудование с таким id.")
                return
        else:
            await update.message.reply_text("Не понял вашу команду. Используйте кнопки меню.")
            
    async def _show_my_equipment(self, update: Update):
        tg_id = update.effective_user.id
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, tg_id)
            items = await self.equipment_service.list_by_owner(session, user.id)

        if not items:
            await update.message.reply_text("У вас пока нет размещённого оборудования.\nНажмите «➕ Добавить оборудование».")
            return

        lines = ["🧰 *Ваше оборудование:*"]
        for i, eq in enumerate(items, start=1):
            lines.append(f"{i}. {eq.name} — {eq.display_status} (id={eq.id})")
        lines.append("\nЧтобы скрыть/показать: отправьте `публикация <id> <on/off>`")
        lines.append("Чтобы добавить бронь: нажмите «➕ Добавить бронь» и следуйте шагам.")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    async def _start_add_equipment_flow(self, update: Update):
        """Запускает пошаговое добавление оборудования для арендодателя."""
        user_id = update.effective_user.id
        # сохраняем состояние диалога
        self.user_states[user_id] = {"state": "add_eq_name", "data": {}}
        await update.message.reply_text("📝 Введите название оборудования:")

    async def _handle_equipment_flow(self, update: Update, message_text: str):
        """Обрабатывает шаги при добавлении оборудования."""
        user_id = update.effective_user.id
        st = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]

        # === 1. Название ===
        if st == "add_eq_name":
            data["name"] = message_text.strip()
            self.user_states[user_id]["state"] = "add_eq_category"
            await update.message.reply_text("📂 Укажите ID категории (1 — звук, 2 — свет, 3 — мебель, 4 — техника):")
            return

        # === 2. Категория ===
        if st == "add_eq_category":
            try:
                data["category_id"] = int(message_text)
            except ValueError:
                await update.message.reply_text("❌ Введите числовой ID категории.")
                return
            self.user_states[user_id]["state"] = "add_eq_city"
            await update.message.reply_text("🏙 Укажите ID города (1 — Самара, 2 — Москва):")
            return

        # === 3. Город ===
        if st == "add_eq_city":
            try:
                data["city_id"] = int(message_text)
            except ValueError:
                await update.message.reply_text("❌ Введите числовой ID города.")
                return
            self.user_states[user_id]["state"] = "add_eq_description"
            await update.message.reply_text("✍️ Введите описание оборудования:")
            return

        # === 4. Описание ===
        if st == "add_eq_description":
            data["description"] = message_text.strip()
            self.user_states[user_id]["state"] = "add_eq_quantity"
            await update.message.reply_text("📦 Укажите количество (число):")
            return

        # === 5. Количество ===
        if st == "add_eq_quantity":
            try:
                qty = int(message_text)
                if qty < 1:
                    raise ValueError
                data["quantity"] = qty
            except ValueError:
                await update.message.reply_text("❌ Введите целое число больше 0.")
                return

            # === 6. Создание записи в БД ===
            async with AsyncSessionLocal() as session:
                owner = await self.user_service.get_user_profile(session, user_id)

                new_equipment = Equipment(
                    name=data["name"],
                    city_id=data["city_id"],
                    user_id=owner.id,
                    category_id=data["category_id"],
                    description=data["description"],
                    quantity=data["quantity"],
                    is_approved=False,   # на модерации
                    is_publish=False,    # пока скрыто
                    created_at=datetime.now(datetime.timezone.utc),
                )

                created = await self.equipment_service.create_equipment(session, new_equipment)

            # очищаем состояние
            del self.user_states[user_id]

            await update.message.reply_text(
                f"✅ Заявка создана и отправлена на модерацию.\n\n"
                f"🆔 ID: {created.id}\n"
                f"📦 Название: {created.name}\n"
                f"📂 Категория: {data['category_id']}\n"
                f"🏙 Город: {data['city_id']}\n"
                f"📄 Описание: {data['description']}\n"
                f"📊 Количество: {data['quantity']}\n\n"
                f"Статус: 🟡 На модерации"
            )

    async def _show_equipment_catalog(self, update: Update):
        await update.message.reply_text("📋 Раздел каталога оборудования в разработке...")

    async def _show_user_profile(self, update: Update):
        tg_id = update.effective_user.id
        async with AsyncSessionLocal() as session:
            user: AppUser = await self.user_service.get_user_profile(session, tg_id)
        city_name = await self.city_service.get_name_city_by_id(session,tg_id)
        if(user.publish):
            publish_text = "Разрешено"
        elif(not user.publish):
            publish_text = "Запрещено"
        else:
            publish_text = "Обратитесь к @admin за разрешением"

        profile_text = (
            f"👤 Ваш профиль:\n"
            f"Разрешение на публикацию: {publish_text}\n"
            f"Имя: {user.name}\n"
            f"Город: {city_name}\n"
            f"Телефон: {user.phone_number or 'не указан'}\n"
            f"Email: {user.email or 'не указан'}"
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

    async def handle_search(self, update: Update):
        """Обработчик кнопки поиска"""
        await self.equipment_bot.search(update)
    # ------------------------ Обработчики для диспетчера ------------------------
    def get_handlers(self):
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self._show_help),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler),
            MessageHandler(filters.CONTACT, self._handle_contact_shared),
            MessageHandler(filters.Regex("^🔍 Поиск$"), self.handle_search)
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

    def _parse_date(self, s: str) -> datetime | None:
        """Парсит дату формата дд.мм.гггг."""
        try:
            return datetime.strptime(s.strip(), "%d.%m.%Y")
        except Exception:
            return None

    async def _start_add_booking_flow(self, update: Update):
        """Запускает процесс добавления брони."""
        uid = update.effective_user.id
        self.user_states[uid] = {
            "state": self.LANDLORD_STATES["ADD_BOOK_EQUIPMENT_ID"],
            "data": {},
        }
        await update.message.reply_text("🆔 Введите ID оборудования для брони:")

    async def _handle_booking_flow(self, update: Update, user_id: int, message_text: str):
        """Пошаговое создание брони."""
        st = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]

        # --- шаг 1: ввод ID оборудования ---
        if st == self.LANDLORD_STATES["ADD_BOOK_EQUIPMENT_ID"]:
            try:
                data["equipment_id"] = int(message_text)
            except ValueError:
                await update.message.reply_text("ID должен быть числом.")
                return

            self.user_states[user_id]["state"] = self.LANDLORD_STATES["ADD_BOOK_DATE_FROM"]
            await update.message.reply_text("📅 Дата С (дд.мм.гггг):")
            return

        # --- шаг 2: дата начала ---
        if st == self.LANDLORD_STATES["ADD_BOOK_DATE_FROM"]:
            dt = self._parse_date(message_text)
            if not dt:
                await update.message.reply_text("❌ Формат даты: дд.мм.гггг")
                return

            data["date_from"] = dt
            self.user_states[user_id]["state"] = self.LANDLORD_STATES["ADD_BOOK_DATE_TO"]
            await update.message.reply_text("📅 Дата ПО (дд.мм.гггг):")
            return

        # --- шаг 3: дата окончания ---
        if st == self.LANDLORD_STATES["ADD_BOOK_DATE_TO"]:
            dt = self._parse_date(message_text)
            if not dt:
                await update.message.reply_text("❌ Формат даты: дд.мм.гггг")
                return

            data["date_to"] = dt

            # --- шаг 4: создание записи в БД ---
            async with AsyncSessionLocal() as session:
                owner = await self.user_service.get_user_profile(session, user_id)
                try:
                    await self.equipment_service._booking_service.create_booking(
                        session,
                        equipment_id=data["equipment_id"],
                        user_id=owner.id,
                        date_from=data["date_from"],
                        date_to=data["date_to"],
                    )
                    await session.commit()
                except Exception as e:
                    await update.message.reply_text(f"❌ Не удалось создать бронь: {e}")
                    del self.user_states[user_id]
                    return

            del self.user_states[user_id]
            await update.message.reply_text("✅ Бронь добавлена.")
            return

    async def _handle_registration_flow(self, update, user_id: int, message_text: str):
        st = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]

        if st == "review_eq_id":
            try:
                data["equipment_id"] = int(message_text)
            except:
                await update.message.reply_text("ID должен быть числом.")
                return
            self.user_states[user_id]["state"] = "review_rating"
            await update.message.reply_text("Оценка 1–5:")
            return

        if st == "review_rating":
            try:
                data["rating"] = int(message_text)
            except:
                await update.message.reply_text("Введите число 1..5.")
                return
            self.user_states[user_id]["state"] = "review_comment"
            await update.message.reply_text("Комментарий (можно пусто):")
            return

        if st == "review_comment":
            comment = message_text if message_text.strip() else None
            async with AsyncSessionLocal() as session:
                renter = await self.user_service.get_user_profile(session, user_id)
                # упрощённо: owner_id достанем по equipment_id
                eq = await self.equipment_service.get_equipment(session, data["equipment_id"])
                if not eq:
                    await update.message.reply_text("Не нашёл оборудование.")
                    del self.user_states[user_id]; return
                await self.review_service.add_review(
                    session,
                    equipment_id=data["equipment_id"],
                    renter_id=renter.id,
                    owner_id=eq.user_id,
                    rating=data["rating"],
                    comment=comment
                )
            del self.user_states[user_id]
            await update.message.reply_text("✅ Отзыв добавлен. Спасибо!")
            return
        
    def _try_int(self, s: str) -> int|None:
        try:
            return int(s)
        except Exception:
            return None

    async def _start_review_flow(self, update: Update, context=None):
        """Стартует флоу отзыва по команде /review."""
        uid = update.effective_user.id
        # заводим состояние
        self.user_states[uid] = {"state": "review_eq_id", "data": {}}
        await update.message.reply_text("📝 Отзыв. Введите ID оборудования:")

    async def _handle_review_flow(self, update: Update, user_id: int, message_text: str):
        """Пошаговая обработка отзывов: equipment_id -> rating -> comment."""
        st = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]

        # 1) запросили ID оборудования
        if st == "review_eq_id":
            eq_id = self._try_int(message_text)
            if not eq_id:
                await update.message.reply_text("ID должен быть числом. Введите ID оборудования:")
                return
            data["equipment_id"] = eq_id
            self.user_states[user_id]["state"] = "review_rating"
            await update.message.reply_text("Оценка 1–5:")
            return

        # 2) оценка
        if st == "review_rating":
            rating = self._try_int(message_text)
            if not rating or rating < 1 or rating > 5:
                await update.message.reply_text("Введите целое число от 1 до 5.")
                return
            data["rating"] = rating
            self.user_states[user_id]["state"] = "review_comment"
            await update.message.reply_text("Комментарий (можно оставить пустым):")
            return

        # 3) комментарий -> запись в БД
        if st == "review_comment":
            comment = message_text.strip() or None
            async with AsyncSessionLocal() as session:
                # текущий пользователь как арендатор
                renter = await self.user_service.get_user_profile(session, user_id)
                # находим владельца по equipment_id
                eq = await self.equipment_service.get_equipment(session, data["equipment_id"])
                if not eq:
                    await update.message.reply_text("Не нашёл оборудование с таким ID.")
                    del self.user_states[user_id]
                    return

                await self.review_service.add_review(
                    session,
                    equipment_id=data["equipment_id"],
                    renter_id=renter.id,
                    owner_id=eq.user_id,
                    rating=data["rating"],
                    comment=comment
                )

            del self.user_states[user_id]
            await update.message.reply_text("✅ Отзыв добавлен. Спасибо!")
            return
