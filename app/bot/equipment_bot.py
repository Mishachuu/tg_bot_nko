from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.services.equipment_service import EquipmentService
from app.bot.equipment_card_formatter import EquipmentCardFormatter
from app.db.session import AsyncSessionLocal

class EquipmentBot:
    def __init__(self, equipment_service: EquipmentService):
        self.equipment_service = equipment_service
        self.formatter = EquipmentCardFormatter()
        self.users = {1: "Иван Петров", 2: "Анна Сидорова", 3: "Петр Иванов"}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        main_keyboard = [
            ["🎒 Моё оборудование"],
            ["📦 Доступное оборудование"], 
            ["➕ Создать оборудование"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "👋 Добро пожаловать в сервис аренды оборудования!\nВыберите действие:",
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        
        if text == "🎒 Моё оборудование":
            await self.show_my_equipment(update, context)
        elif text == "📦 Доступное оборудование":
            await self.show_available_equipment(update, context)
        elif text == "➕ Создать оборудование":
            await update.message.reply_text("🛠️ Функция создания оборудования в разработке...")
        else:
            await update.message.reply_text("🤔 Не понимаю команду. Используйте кнопки меню.")
    
    async def show_my_equipment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        async with AsyncSessionLocal() as session:
            all_equipment = await self.equipment_service.list_equipment(session)

        my_equipment = [eq for eq in all_equipment if eq.landlord_id == 1]
        
        if not my_equipment:
            await update.message.reply_text("📭 У вас пока нет оборудования.")
            return
        
        await update.message.reply_text(f"🎒 Ваше оборудование ({len(my_equipment)} позиций):")
        
        for equipment in my_equipment:
            card_text = self.formatter.create_equipment_card(
                equipment, 
                self.users.get(equipment.landlord_id, "Вы")
            )
            await update.message.reply_text(card_text, parse_mode='Markdown')
    
    async def show_available_equipment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        async with AsyncSessionLocal() as session:
            all_equipment = await self.equipment_service.list_equipment(session)
        available_equipment = [
            eq for eq in all_equipment 
            if eq.landlord_id != 1 and eq.status.value == "available"
        ]
        
        if not available_equipment:
            await update.message.reply_text("😔 Сейчас нет доступного оборудования.")
            return
        
        await update.message.reply_text(f"📦 Доступное оборудование ({len(available_equipment)} позиций):")
        
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
            await query.edit_message_text(f"📋 Бронирование оборудования ID: {equipment_id}\nФункция бронирования в разработке...")
        elif callback_data.startswith('ask_'):
            equipment_id = int(callback_data.split('_')[1])
            await query.edit_message_text(f"💬 Вопрос по оборудованию ID: {equipment_id}\nФункция вопросов в разработке...")
    
    def get_handlers(self):
        """Возвращает список обработчиков для регистрации"""
        return [
            CommandHandler("start", self.start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            CallbackQueryHandler(self.handle_callback)
        ]