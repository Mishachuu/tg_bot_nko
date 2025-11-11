from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models.equipment import  Equipment

class EquipmentCardFormatter:
    """Форматирует карточки оборудования для Telegram"""
    
    @classmethod
    def create_equipment_card(cls, equipment: Equipment, landlord_name: str = "Неизвестно", category: str = "Не указано") -> str:
        """Создает форматированную карточку оборудования"""
        
        card_lines = [
            f"*{equipment.name or 'Без названия'}*",
            f"Описание: {equipment.description or 'Нет описания'}",
            f"Количество: {equipment.quantity} шт.",
            f"Категория: {category}",
            f"Арендодатель: {landlord_name}"
        ]
        
        return "\n".join(card_lines)