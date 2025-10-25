from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models.equipment import RentalStatus, Equipment

class EquipmentCardFormatter:
    """Форматирует карточки оборудования для Telegram"""
    
    STATUS_EMOJIS = {
        RentalStatus.AVAILABLE: "✅ Доступен",
        RentalStatus.BOOKED: "⏳ Забронирован", 
        RentalStatus.IN_USE: "🔴 В аренде",
        RentalStatus.RETURNED: "🔄 Возвращен"
    }
    
    @classmethod
    def format_status(cls, status: RentalStatus) -> str:
        """Форматирует статус с эмодзи"""
        return cls.STATUS_EMOJIS.get(status, "❓ Неизвестно")
    
    @classmethod
    def create_equipment_card(cls, equipment: Equipment, landlord_name: str = "Неизвестно") -> str:
        """Создает форматированную карточку оборудования"""
        
        card_lines = [
            f"🎯 *{equipment.name or 'Без названия'}*",
            f"📝 * _Описание:_ * {equipment.description or 'Нет описания'}",
            f"📦 Количество: {equipment.quantity=} шт.",
            f"🏙️ Город: {cls._get_city_name(equipment.city_id)}",
            f"📂 Категория: {cls._get_category_name(equipment.category_id)}",
            f"📊 Статус: {cls.format_status(equipment.status)}",
            f"👤 Арендодатель: {landlord_name}"
        ]
        
        return "\n".join(card_lines)
    
    @classmethod
    def create_interaction_keyboard(cls, equipment_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру для взаимодействия с оборудованием"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Забронировать", callback_data=f"book_{equipment_id}"),
                InlineKeyboardButton("💬 Задать вопрос", callback_data=f"ask_{equipment_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def _get_city_name(cls, city_id: int) -> str:
        """Получить название города по ID (заглушка)"""
        cities = {
            1: "Москва",
            2: "Санкт-Петербург", 
            3: "Новосибирск",
            4: "Екатеринбург",
            5: "Казань"
        }
        return cities.get(city_id, "Не указан")
    
    @classmethod
    def _get_category_name(cls, category_id: int) -> str:
        """Получить название категории по ID (заглушка)"""
        categories = {
            1: "🎵 Звуковое оборудование",
            2: "💡 Световое оборудование", 
            3: "🪑 Мебель и конструкции",
            4: "🎥 Видео оборудование",
            5: "🔧 Инструменты"
        }
        return categories.get(category_id, "Другое")