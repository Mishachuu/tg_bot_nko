from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.db.session import AsyncSessionLocal
from app.models.equipment import Equipment
from app.services.category_service import CategoryService
from app.services.equipment_service import EquipmentService
from app.services.user_service import UserService
from app.repositories.category_repository import CategoryRepository
from app.bot.equipment_card_formatter import EquipmentCardFormatter
from app.helpers.gis_helper import calculate_distance
from datetime import datetime
from app.models.user_app import AppUser

import io


class MainBot:
    def __init__(self, user_service:UserService, equipment_service, booking_service, review_service, category_service, equipment_photo_service):
        self.user_service = user_service
        self.equipment_service = equipment_service
        self.booking_service = booking_service
        self.review_service = review_service
        self.category_service = category_service
        self.equipment_photo_service = equipment_photo_service
        self.formatter = EquipmentCardFormatter()
        
        self.user_states = {}
        self.SEARCH_STATES = {
            "ASKING_LOCATION": "asking_location",
            "ASKING_RADIUS": "asking_radius",
            "CHOOSING_CATEGORIES": "choosing_categories",
            "ENTERING_DATE_FROM": "entering_date_from",
            "ENTERING_DATE_TO": "entering_date_to"
        }
        
        self.REGISTRATION_STATES = {
            "WAITING_FOR_NAME": "waiting_for_name",
            "WAITING_FOR_PHONE": "waiting_for_phone", 
            "WAITING_FOR_EMAIL": "waiting_for_email"
        }
        
        self.EQUIPMENT_STATES = {
            "ADD_NAME": "add_equipment_name",
            "ADD_DESCRIPTION": "add_equipment_description", 
            "CHOOSING_CATEGORY": "choosing_category",
            "ADD_QUANTITY": "add_equipment_quantity",
            "ADD_LOCATION": "add_equipment_location",
            "ADD_PHOTOS": "add_equipment_photos"
        }

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главный обработчик всех сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Проверяем регистрацию
        async with AsyncSessionLocal() as session:
            is_registered = await self.user_service.check_user(session, user_id)
            
        if not is_registered:
            await self._handle_registration(update, user_id, message_text)
            return
            
        # Если пользователь зарегистрирован, обрабатываем команды
        await self._handle_commands(update, context, user_id, message_text)

    async def _handle_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, message_text: str):
        """Обработка команд после регистрации"""
        # Проверяем, находится ли пользователь в каком-либо состоянии
        if user_id in self.user_states:
            await self._handle_states(update, context, user_id, message_text)
            return
            
        # Обработка основных команд меню
        if message_text == "🔍 Найти оборудование":
            await self._start_search_flow(update,context , user_id)
            
        elif message_text == "➕ Добавить оборудование":
            await self._check_lessor_and_start_equipment_flow(update, user_id)
            
        elif message_text == "🛠️ Моё оборудование":
            await self._check_lessor_and_show_equipment(update, user_id)
            
        elif message_text == "📋 Мои бронирования":
            await self._show_my_bookings(update, user_id)
            
        else:
            await update.message.reply_text("Не понял команду. Используйте кнопки меню.")

    async def _handle_registration(self, update: Update, user_id: int, message_text: str):
        """Обработка процесса регистрации"""
        message = update.message or update.callback_query.message
        if user_id not in self.user_states:
            # Начинаем регистрацию
            self.user_states[user_id] = {
                "state": self.REGISTRATION_STATES["WAITING_FOR_NAME"],
                "data": {}
            }
            await message.reply_text(
                "👋 Добро пожаловать! Для начала работы нужно зарегистрироваться.\n"
                "Введите ваше имя:",
                reply_markup=ReplyKeyboardRemove()
            )
            return
            
        state = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]
        
        if state == self.REGISTRATION_STATES["WAITING_FOR_NAME"]:
            data["name"] = message_text
            self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_PHONE"]
            
            phone_keyboard = [[KeyboardButton("📱 Отправить телефон", request_contact=True)]]
            await message.reply_text(
                "📞 Отправьте ваш номер телефона:",
                reply_markup=ReplyKeyboardMarkup(phone_keyboard, resize_keyboard=True)
            )
            
        elif state == self.REGISTRATION_STATES["WAITING_FOR_PHONE"]:
            data["phone"] = message_text
            self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_EMAIL"]
            await message.reply_text("📧 Введите ваш email (или 'пропустить'):")
            
        elif state == self.REGISTRATION_STATES["WAITING_FOR_EMAIL"]:
            if message_text.lower() != 'пропустить':
                data["email"] = message_text
                
            # Завершаем регистрацию
            async with AsyncSessionLocal() as session:
                await self.user_service.create_user(
                    session=session,
                    tg_id=user_id,
                    name=data["name"],
                    phone_number=data.get("phone"),
                    email=data.get("email")
                )
                
            del self.user_states[user_id]
            await self._show_main_menu(update, user_id, "✅ Регистрация завершена!")

    async def _handle_states(self, update: Update,context: ContextTypes.DEFAULT_TYPE, user_id: int, message_text: str):
        """Обработка различных состояний"""
        if user_id not in self.user_states:
            await update.message.reply_text("Не понял команду. Используйте кнопки меню.")
            return
            
        state = self.user_states[user_id]["state"]
        data = self.user_states[user_id]["data"]
        
        # Обработка состояний поиска
        if state in [self.SEARCH_STATES["ASKING_RADIUS"], 
                    self.SEARCH_STATES["CHOOSING_CATEGORIES"],
                    self.SEARCH_STATES["ENTERING_DATE_FROM"], 
                    self.SEARCH_STATES["ENTERING_DATE_TO"]]:
            await self._handle_search_flow(update, context, user_id, message_text, state, data)
            
        # Обработка состояний добавления оборудования
        elif state in [self.EQUIPMENT_STATES["ADD_NAME"],
                    self.EQUIPMENT_STATES["ADD_DESCRIPTION"], 
                    self.EQUIPMENT_STATES["ADD_QUANTITY"],
                    self.EQUIPMENT_STATES["ADD_PHOTOS"]]:
            await self._handle_equipment_flow(update, user_id, message_text, state, data)
            
        # Обработка выбора категории для оборудования
        elif state == self.EQUIPMENT_STATES["CHOOSING_CATEGORY"]:
            await self._handle_category_selection(update, user_id, message_text, data)
            
        else:
            await update.message.reply_text("Не понял команду. Используйте кнопки меню.")

    # ========== ПОИСК ОБОРУДОВАНИЯ ==========
    async def _start_search_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Начинает процесс поиска оборудования"""
        self.user_states[user_id] = {
            "state": self.SEARCH_STATES["ASKING_LOCATION"],
            "data": {
                "selected_categories": set(),
                "date_from": None,
                "date_to": None,
                "location": None,
                "radius_km": 30
            }
        }
        
        location_keyboard = [[KeyboardButton("📍 Отправить локацию", request_location=True)]]
        await update.message.reply_text(
            "📍 Для поиска оборудования отправьте вашу локацию:",
            reply_markup=ReplyKeyboardMarkup(location_keyboard, resize_keyboard=True)
        )

    async def _handle_search_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, message_text: str, state: str, data: dict):
        """Обработка шагов поиска оборудования"""
        if state == self.SEARCH_STATES["ASKING_RADIUS"]:
            try:
                if message_text:
                    radius = int(message_text)
                    if radius <= 0:
                        raise ValueError
                    data["radius_km"] = radius
                else:
                    data["radius_km"] = 30
                    
                self.user_states[user_id]["state"] = self.SEARCH_STATES["CHOOSING_CATEGORIES"]
                await self._ask_categories(update, user_id, data["selected_categories"])
                
            except ValueError:
                await update.message.reply_text("⚠️ Введите число километров, например 15:")

        elif state == self.SEARCH_STATES["CHOOSING_CATEGORIES"]:
            if message_text == "🔍 Найти":
                if not data["selected_categories"]:
                    await update.message.reply_text("❗ Выберите хотя бы одну категорию.")
                    return
                self.user_states[user_id]["state"] = self.SEARCH_STATES["ENTERING_DATE_FROM"]
                await update.message.reply_text("Введите дату начала аренды (ГГГГ.ММ.ДД):")
            else:
                await self._toggle_category_selection(update, message_text, data)

        elif state == self.SEARCH_STATES["ENTERING_DATE_FROM"]:
            try:
                data["date_from"] = datetime.strptime(message_text, "%Y.%m.%d")
                self.user_states[user_id]["state"] = self.SEARCH_STATES["ENTERING_DATE_TO"]
                await update.message.reply_text("Введите дату окончания аренды (ГГГГ.ММ.ДД):")
            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат. Введите дату как ГГГГ.ММ.ДД.")

        elif state == self.SEARCH_STATES["ENTERING_DATE_TO"]:
            try:
                data["date_to"] = datetime.strptime(message_text, "%Y.%m.%d")
                if data["date_to"] < data["date_from"]:
                    await update.message.reply_text("⚠️ Дата окончания не может быть раньше даты начала.")
                    return
                    
                await self._show_equipment_by_categories_and_date(update, context, user_id, data)
                del self.user_states[user_id]  # Завершаем процесс поиска
                
            except ValueError:
                await update.message.reply_text("⚠️ Неверный формат даты. Введите дату снова.")

    async def _ask_categories(self, update: Update, user_id: int, selected_categories: set):
        """Запрашивает выбор категорий"""
        async with AsyncSessionLocal() as session:
            categories = await self.category_service.list_categories(session)

        if not categories:
            await update.message.reply_text("⚠️ В базе нет категорий.")
            return

        keyboard = []
        for category in categories:
            name = category.name
            if category.id in selected_categories:
                display_name = f"✅ {name}"
            else:
                display_name = name
            keyboard.append([display_name])

        keyboard.append(["🔍 Найти"])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📂 Выберите категории (можно несколько):", reply_markup=reply_markup)

    async def _toggle_category_selection(self, update: Update, text: str, data: dict):
        """Переключает выбор категории"""
        if text.startswith("✅ "):
            category_name = text[2:].strip()
        else:
            category_name = text.strip()

        async with AsyncSessionLocal() as session:
            categories = await self.category_service.list_categories(session)

        category = next((c for c in categories if c.name == category_name), None)
        if not category:
            await update.message.reply_text("❌ Неизвестная категория. Попробуйте снова.")
            return

        cat_id = category.id
        if cat_id in data["selected_categories"]:
            data["selected_categories"].remove(cat_id)
        else:
            data["selected_categories"].add(cat_id)

        await self._ask_categories(update, update.effective_user.id, data["selected_categories"])

    async def _show_equipment_by_categories_and_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, data: dict):
        """Показывает найденное оборудование с фото в одном сообщении"""
        async with AsyncSessionLocal() as session:
            available_equipment = []
            
            user_location = data.get("location")
            radius_km = data.get("radius_km", 30)
            
            for cat_id in data["selected_categories"]:
                eqs = await self.equipment_service.find_available_by_category_date_and_location(
                    session,
                    cat_id,
                    data["date_from"],
                    data["date_to"],
                    user_location["lat"],
                    user_location["lon"],
                    radius_km
                )
                available_equipment.extend(eqs)

            if not available_equipment:
                location_info = ""
                if user_location:
                    location_info = f" в радиусе {radius_km} км от вашей локации"
                
                await update.message.reply_text(
                    f"😔 Нет свободного оборудования на выбранные даты{location_info}.",
                    reply_markup=ReplyKeyboardRemove()
                )
                await self._show_main_menu(update, user_id)
                return

            location_info = ""
            if user_location:
                location_info = f" в радиусе {radius_km} км от вас"
                
            await update.message.reply_text(
                f"📦 Доступное оборудование{location_info} ({len(available_equipment)} позиций):",
                reply_markup=ReplyKeyboardRemove()
            )

            for eq in available_equipment:
                # Получаем название категории из базы данных
                category_name = await self._get_category_name(session, eq.category_id)
                
                # Получаем фото оборудования
                photos = await self.equipment_photo_service.list_photos(session, eq.id)
                # Полдучаем пользователя 
                
                user: AppUser = await self.user_service.get_user_by_id(session, eq.user_id)

                if user and user.tg_id:
                    try:
                        tguser = await context.bot.get_chat(user.tg_id)  
                        username = tguser.username
                        owner_info = f" @{username}" if username else " Неизвестен"
                    except Exception as e:
                        owner_info = " Недоступен"
                else:
                    owner_info = " Не указан"

                card_text = self.formatter.create_equipment_card(
                    eq, 
                    owner_info,
                    category_name
)
                
                if user_location and eq.latitude and eq.longitude:
                    distance = calculate_distance(
                        user_location["lat"], user_location["lon"],
                        eq.latitude, eq.longitude
                    )
                    card_text += f"\n📍 Расстояние: {distance:.1f} км"
                
                # Если есть фото, отправляем все фото одним сообщением с текстом
                if photos:
                    await self._send_equipment_with_photos(update, eq, card_text, photos)
                else:
                    # Если фото нет, отправляем только текст с кнопками
                    await update.message.reply_text(
                        card_text, 
                        parse_mode='Markdown'
                    )

            await self._show_main_menu(update, user_id)
   
    async def _send_photos_individually(self, update: Update, photos: list, caption: str):
        """Отправляет фото по одному (запасной метод)"""
        if photos:
            first_photo = photos[0]
            photo_file = InputFile(io.BytesIO(first_photo.photo_data), filename=first_photo.filename)
            await update.message.reply_photo(
                photo=photo_file,
                caption=caption,
                parse_mode='Markdown'
            )
            
            for additional_photo in photos[1:]:
                additional_photo_file = InputFile(
                    io.BytesIO(additional_photo.photo_data), 
                    filename=additional_photo.filename
                )
                await update.message.reply_photo(photo=additional_photo_file)

    async def _get_category_name(self, session, category_id: int) -> str:
        """Получает название категории по ID из базы данных"""
        if not category_id:
            return "Не указано"
        
        try:
            category = await self.category_service.get_by_id(session, category_id)
            return category.name if category else "Неизвестная категория"
        except Exception as e:
            print(f"Ошибка при получении категории {category_id}: {e}")
            return "Неизвестная категория"

    # ========== УПРАВЛЕНИЕ ОБОРУДОВАНИЕМ (для арендодателей) ==========
    async def _check_lessor_and_start_equipment_flow(self, update: Update, user_id: int):
        """Проверяет права арендодателя и начинает процесс добавления оборудования"""
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)
            
        if not user.is_lessor:
            await update.message.reply_text(
                "❌ У вас нет прав на добавление оборудования.\n"
                "Обратитесь к администратору для получения прав арендодателя."
            )
            return
            
        self.user_states[user_id] = {
            "state": self.EQUIPMENT_STATES["ADD_NAME"],
            "data": {}
        }
        await update.message.reply_text(
            "📝 Введите название оборудования:",
            reply_markup=ReplyKeyboardRemove()
        )

    async def _check_lessor_and_show_equipment(self, update: Update, user_id: int):
        """Показывает оборудование арендодателя с фото в одном сообщении"""
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)
            
        if not user.is_lessor:
            await update.message.reply_text("❌ У вас нет оборудования.")
            return
            
        async with AsyncSessionLocal() as session:
            equipment_list = await self.equipment_service.list_by_owner(session, user.id)
            
        if not equipment_list:
            await update.message.reply_text("У вас пока нет оборудования.")
            return
            
        await update.message.reply_text(f"🛠️ Ваше оборудование ({len(equipment_list)} позиций):")
        
        for equipment in equipment_list:
            # Получаем фото оборудования
            async with AsyncSessionLocal() as session:
                photos = await self.equipment_photo_service.list_photos(session, equipment.id)
            
            # Создаем карточку оборудования
            category_name = await self._get_category_name(session, equipment.category_id)
            card_text = self.formatter.create_equipment_card(
                equipment, 
                f"Вы (ID: {user.id})", # нах нам тут user.id ? 
                category_name
            )
            
            # Если есть фото, отправляем их медиагруппой с текстом
            if photos:
                await self._send_equipment_with_photos(update, equipment, card_text, photos)
            else:
                # Если фото нет, отправляем просто текст
                await update.message.reply_text(card_text, parse_mode='Markdown')

    async def _send_equipment_with_photos(self, update: Update, equipment, card_text: str, photos: list):
        """Отправляет оборудование с фото в одном сообщении"""
        try:            
            media_group = []
            
            for i, photo_data in enumerate(photos):
                photo_content = photo_data.get("content")
                
                if photo_content:
                    if isinstance(photo_content, memoryview):
                        photo_content = photo_content.tobytes()
                    
                    media = InputMediaPhoto(
                        media=photo_content,
                        caption=card_text if i == 0 else None
                    )
                    media_group.append(media)
                else:
                    print(f"⚠️ Нет content для фото {photo_data.get('id')} оборудования {equipment.id}")
            
            if media_group:
                await update.message.reply_media_group(media=media_group)
            else:
                # Если не удалось создать медиагруппу, отправляем просто текст
                await update.message.reply_text(card_text, parse_mode='Markdown')
                
        except Exception as e:
            print(f"❌ Ошибка при отправке фото оборудования {equipment.id}: {e}")
            # Fallback: отправляем текст и фото по отдельности
            await update.message.reply_text(card_text, parse_mode='Markdown')
            for photo_data in photos:
                photo_content = photo_data.get("content")
                if photo_content:
                    if isinstance(photo_content, memoryview):
                        photo_content = photo_content.tobytes()
                    try:
                        await update.message.reply_photo(photo=photo_content)
                    except Exception as photo_error:
                        print(f"❌ Ошибка при отправке отдельного фото: {photo_error}")
    
    async def _handle_equipment_flow(self, update: Update, user_id: int, message_text: str, state: str, data: dict):
        """Обработка шагов добавления оборудования"""
        if state == self.EQUIPMENT_STATES["ADD_NAME"]:
            data["name"] = message_text
            self.user_states[user_id]["state"] = self.EQUIPMENT_STATES["ADD_DESCRIPTION"]
            await update.message.reply_text("✍️ Введите описание оборудования:")
            
        elif state == self.EQUIPMENT_STATES["ADD_DESCRIPTION"]:
            data["description"] = message_text
            self.user_states[user_id]["state"] = self.EQUIPMENT_STATES["CHOOSING_CATEGORY"]
            await self._ask_categories_for_equipment(update, user_id)
            
        elif state == self.EQUIPMENT_STATES["ADD_QUANTITY"]:
            try:
                quantity = int(message_text)
                if quantity <= 0:
                    raise ValueError
                data["quantity"] = quantity
                self.user_states[user_id]["state"] = self.EQUIPMENT_STATES["ADD_LOCATION"]
                
                location_keyboard = [[KeyboardButton("📍 Отправить локацию", request_location=True)]]
                await update.message.reply_text(
                    "📍 Отправьте локацию, откуда можно забрать оборудование:",
                    reply_markup=ReplyKeyboardMarkup(location_keyboard, resize_keyboard=True)
                )
            except ValueError:
                await update.message.reply_text("❌ Введите корректное количество (число больше 0):")
                
        elif state == self.EQUIPMENT_STATES["ADD_PHOTOS"]:
            if message_text.lower() == "готово":
                photo_count = len(data.get("photos", []))
                if photo_count == 0:
                    # Спрашиваем подтверждение если фото нет
                    confirm_keyboard = ReplyKeyboardMarkup([["Да, без фото", "Добавить фото"]], resize_keyboard=True)
                    await update.message.reply_text(
                        "Вы не добавили ни одного фото. Продолжить без фото?",
                        reply_markup=confirm_keyboard
                    )
                    data["awaiting_photo_confirmation"] = True
                else:
                    await self._create_equipment(update, user_id, data)
            elif data.get("awaiting_photo_confirmation"):
                if message_text.lower() == "да, без фото":
                    await self._create_equipment(update, user_id, data)
                else:
                    data["awaiting_photo_confirmation"] = False
                    await update.message.reply_text("📸 Отправьте фотографии оборудования:")
            else:
                await update.message.reply_text(
                    "📸 Отправьте фотографии оборудования или нажмите 'Готово' чтобы завершить:"
                )

    async def _create_equipment(self, update: Update, user_id: int, data: dict):
        """Создает оборудование в БД с фото"""
        async with AsyncSessionLocal() as session:
            try:
                # Получаем пользователя
                user = await self.user_service.get_user_profile(session, user_id)
                
                # Создаем объект Equipment вместо словаря
                equipment = Equipment(
                    name=data["name"],
                    description=data["description"],
                    user_id=user.id,
                    category_id=data["category_id"],
                    quantity=data["quantity"],
                    latitude=data.get("latitude"),
                    longitude=data.get("longitude"),
                    is_approved=False,  # На модерации
                    is_publish=False,
                    created_at=datetime.now()  # Явно устанавливаем дату создания
                )
                
                # Передаем объект Equipment в сервис
                created_equipment = await self.equipment_service.create_equipment(session, equipment)
                
                # Добавляем фото если есть
                if "photos" in data and data["photos"]:
                    for photo_data in data["photos"]:
                        await self.equipment_photo_service.add_photo(
                            session, 
                            created_equipment.id, 
                            photo_data["filename"], 
                            bytes(photo_data["content"])
                        )
                
                await session.commit()
                
                # Формируем сообщение об успехе
                message = (
                    "✅ Оборудование успешно создано и отправлено на модерацию!\n\n"
                    f"📦 *{data['name']}*\n"
                    f"📝 {data['description']}\n"
                    f"📂 Категория: {data['category_name']}\n"
                    f"📊 Количество: {data['quantity']} шт.\n"
                    f"📍 Локация: {'указана' if data.get('latitude') else 'не указана'}\n"
                    f"📸 Фото: {len(data.get('photos', []))} шт.\n\n"
                    f"🆔 ID оборудования: {created_equipment.id}\n"
                    "⏳ Статус: 🟡 На модерации"
                )
                
                # ОЧИСТКА СОСТОЯНИЯ ПОСЛЕ УСПЕШНОГО СОЗДАНИЯ
                if user_id in self.user_states:
                    del self.user_states[user_id]
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=ReplyKeyboardRemove()
                )
                
                # Показываем главное меню
                await self._show_main_menu(update, user_id)
                
            except Exception as e:
                await session.rollback()
                # ТАКЖЕ ОЧИЩАЕМ СОСТОЯНИЕ ПРИ ОШИБКЕ
                if user_id in self.user_states:
                    del self.user_states[user_id]
                    
                await update.message.reply_text(
                    f"❌ Ошибка при создании оборудования: {e}",
                    reply_markup=ReplyKeyboardRemove()
                )
                await self._show_main_menu(update, user_id)
   
    async def handle_equipment_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает получение фото для оборудования"""
        user_id = update.effective_user.id
        
        if (user_id in self.user_states and 
            self.user_states[user_id]["state"] == self.EQUIPMENT_STATES["ADD_PHOTOS"]):
            
            photo = update.message.photo[-1]  # Берем самое качественное фото
            data = self.user_states[user_id]["data"]
            
            # Сохраняем информацию о фото (будем добавлять в БД при создании оборудования)
            if "photos" not in data:
                data["photos"] = []
                
            # Скачиваем фото
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            data["photos"].append({
                "filename": f"equipment_photo_{len(data['photos']) + 1}.jpg",
                "content": photo_bytes
            })
            
            await update.message.reply_text(
                f"✅ Фото добавлено! Добавлено фото: {len(data['photos'])}\n"
                "Можете отправить еще фото или нажмите 'Готово' чтобы завершить."
            )

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка получения локации для поиска И для оборудования"""
        user_id = update.effective_user.id
        
        # Обработка локации для поиска оборудования
        if (user_id in self.user_states and 
            self.user_states[user_id]["state"] == self.SEARCH_STATES["ASKING_LOCATION"]):
            
            location = update.message.location
            self.user_states[user_id]["data"]["location"] = {
                "lat": location.latitude,
                "lon": location.longitude
            }
            self.user_states[user_id]["state"] = self.SEARCH_STATES["ASKING_RADIUS"]
            
            await update.message.reply_text(
                "📏 Укажите радиус поиска в километрах (по умолчанию 30 км):",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Обработка локации для добавления оборудования
        elif (user_id in self.user_states and 
            self.user_states[user_id]["state"] == self.EQUIPMENT_STATES["ADD_LOCATION"]):
            
            location = update.message.location
            data = self.user_states[user_id]["data"]
            data["latitude"] = location.latitude
            data["longitude"] = location.longitude
            
            self.user_states[user_id]["state"] = self.EQUIPMENT_STATES["ADD_PHOTOS"]
            
            await update.message.reply_text(
                "✅ Локация сохранена!\n\n"
                "📸 Теперь отправьте фотографии оборудования (можно несколько).\n"
                "Когда закончите, нажмите 'Готово'.",
                reply_markup=ReplyKeyboardMarkup([["Готово"]], resize_keyboard=True)
            )

    async def _handle_category_selection(self, update: Update, user_id: int, message_text: str, data: dict):
        """Обрабатывает выбор категории"""
        async with AsyncSessionLocal() as session:
            categories = await self.category_service.list_categories(session)

        category = next((c for c in categories if c.name == message_text), None)
        if not category:
            # Если категория не найдена, показываем клавиатуру снова с сообщением об ошибке
            await update.message.reply_text("❌ Неизвестная категория. Пожалуйста, выберите категорию из списка ниже:")
            await self._ask_categories_for_equipment(update, user_id)
            return

        data["category_id"] = category.id
        data["category_name"] = category.name
        self.user_states[user_id]["state"] = self.EQUIPMENT_STATES["ADD_QUANTITY"]
        
        await update.message.reply_text(
            f"✅ Выбрана категория: {category.name}\n\n"
            "📦 Укажите доступное количество штук:",
            reply_markup=ReplyKeyboardRemove()
        )

    async def _ask_categories_for_equipment(self, update: Update, user_id: int):
        """Запрашивает выбор категории для оборудования"""
        async with AsyncSessionLocal() as session:
            categories = await self.category_service.list_categories(session)

        if not categories:
            await update.message.reply_text("⚠️ В базе нет категорий.")
            return

        keyboard = []
        for category in categories:
            keyboard.append([category.name])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📂 Выберите категорию оборудования:", reply_markup=reply_markup)

    # ========== ОБЩИЕ ФУНКЦИИ ==========
    async def _show_my_bookings(self, update: Update, user_id: int):
        """Показывает бронирования пользователя"""
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)
            bookings = await self.booking_service.get_user_bookings(session, user.id)
            
        if not bookings:
            await update.message.reply_text("У вас пока нет бронирований.")
            return
            
        response = "📋 Ваши бронирования:\n\n"
        for booking in bookings:
            response += f"• ID {booking.id}: {booking.date_from} - {booking.date_to}\n"
            
        await update.message.reply_text(response)

    async def _show_main_menu(self, update: Update, user_id: int, message: str = ""):
        """Показывает главное меню"""
        async with AsyncSessionLocal() as session:
            user : AppUser = await self.user_service.get_user_profile(session, user_id)
        if user.is_lessor:
            menu_buttons = [
                ["🔍 Найти оборудование"],
                ["➕ Добавить оборудование", "🛠️ Моё оборудование"],
                ["📋 Мои бронирования"]
            ]
        else:
            menu_buttons = [
                ["🔍 Найти оборудование"],
                ["📋 Мои бронирования"]
            ]
            
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        text = message or "Выберите действие:"
        await update.message.reply_text(text, reply_markup=reply_markup)

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка получения контакта"""
        user_id = update.effective_user.id
        
        if (user_id in self.user_states and 
            self.user_states[user_id]["state"] == self.REGISTRATION_STATES["WAITING_FOR_PHONE"]):
            
            contact = update.message.contact
            self.user_states[user_id]["data"]["phone"] = contact.phone_number
            self.user_states[user_id]["state"] = self.REGISTRATION_STATES["WAITING_FOR_EMAIL"]
            await update.message.reply_text(
                "📧 Введите ваш email (или 'пропустить'):",
                reply_markup=ReplyKeyboardRemove()
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback'ов"""
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data.startswith('book_'):
            equipment_id = int(callback_data.split('_')[1])
            await query.edit_message_text(f"📋 Бронирование оборудования ID: {equipment_id}")
        elif callback_data.startswith('ask_'):
            equipment_id = int(callback_data.split('_')[1])
            await query.edit_message_text(f"💬 Вопрос по оборудованию ID: {equipment_id}")

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        
        async with AsyncSessionLocal() as session:
            is_registered = await self.user_service.check_user(session, user_id)
            
        if is_registered:
            await self._show_main_menu(update, user_id, "С возвращением!")
        else:
            await self._show_personal_data_consent(update, user_id)

    async def _show_personal_data_consent(self, update: Update, user_id: int):
        """Показать согласие на обработку персональных данных"""
        text = self.formatter.personal_data_consent

        keyboard = [[InlineKeyboardButton("✅ Согласен", callback_data="consent_personal_data")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = update.message or update.callback_query.message
        await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _show_risk_warning(self, update: Update, user_id: int):
        """Показать предупреждение о рисках"""
        text =  self.formatter.risk_warning
        keyboard = [[InlineKeyboardButton("✅ Подтверждаю", callback_data="consent_risk_warning")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = update.message or update.callback_query.message
        await message.reply_text(

            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_personal_data_consent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик согласия на обработку персональных данных"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)  # Убираем кнопку
        
        # Показываем второе согласие
        await self._show_risk_warning(update, user_id)

    async def handle_risk_warning_consent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик подтверждения предупреждения о рисках"""
        query = update.callback_query
        
        
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)  # Убираем кнопку
        
        # Переходим к регистрации 
        await self._handle_registration(update, update.effective_user.id , "Соглашеия подтверждены!\n Добро пожаловать!")


    def get_handlers(self):
        return [
            CommandHandler("start", self.handle_start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            MessageHandler(filters.LOCATION, self.handle_location),
            MessageHandler(filters.CONTACT, self.handle_contact),
            CallbackQueryHandler(self.handle_callback, pattern=r"^(book_|ask_)"),
            MessageHandler(filters.PHOTO & ~filters.COMMAND, self.handle_equipment_photo),
            CallbackQueryHandler(self.handle_personal_data_consent, pattern="^consent_personal_data$"),
            CallbackQueryHandler(self.handle_risk_warning_consent, pattern="^consent_risk_warning$")
        ]