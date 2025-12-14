from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models.equipment import Equipment, EquipmentStatus

MAX_TELEGRAM_MESSAGE_LEN = 4000  # Telegram лимит для текста сообщения

class EquipmentCardFormatter:
    """Форматирует карточки оборудования для Telegram с защитой от ошибок"""

    @classmethod
    def create_equipment_card(
        cls,
        equipment: Equipment,
        landlord_name: str = "Неизвестно",
        category: str = "Не указано",
        available_quantity: Optional[int] = None
    ) -> str:
        """Создает безопасную форматированную карточку оборудования"""
        # Безопасная обработка None и спецсимволов Markdown
        name = equipment.name or "Без названия"
        description = equipment.description or "Нет описания"
        landlord_name = landlord_name or "Неизвестно"

        card_lines = [
            f"*{name}*",
            f"Описание: {description}",
            f"Категория: {category}",
            f"Арендодатель: {landlord_name}",
            f"Всего доступно: {equipment.quantity} шт."
        ]

        if available_quantity is not None:
            card_lines.append(f"📦 Свободно на выбранные даты: *{available_quantity} шт.*")

        card_text = "\n".join(card_lines)

        # Защита от превышения лимита Telegram
        if len(card_text) > MAX_TELEGRAM_MESSAGE_LEN:
            card_text = card_text[:MAX_TELEGRAM_MESSAGE_LEN - 10] + "\n…"

        return card_text

    @classmethod
    def create_my_equipment_card(
        cls,
        equipment: Equipment,
        landlord_name: str = "Неизвестно",
        category: str = "Не указано"
    ) -> str:
        """Создает безопасную карточку собственного оборудования с модерацией"""
        name = equipment.name or "Без названия"
        description = equipment.description or "Нет описания"
        landlord_name = landlord_name or "Неизвестно"

        # Модерация
        if equipment.status == EquipmentStatus.APPROVED:
            moderation_text = "Модерация: Пройдена🟢"
        elif equipment.status == EquipmentStatus.REJECTED:
            reason = equipment.rejection_reason or "Причина не указана"
            moderation_text = f"Модерация: НЕ пройдена🔴\nПричина: {reason}"
        else:
            moderation_text = "Модерация: Ожидайте ⏳"

        card_lines = [
            f"*{name}*",
            f"Описание: {description}",
            f"Количество: {equipment.quantity} шт.",
            f"Категория: {category}",
            f"Арендодатель: {landlord_name}",
            moderation_text
        ]

        card_text = "\n".join(card_lines)

        # Защита от лимита Telegram
        if len(card_text) > MAX_TELEGRAM_MESSAGE_LEN:
            card_text = card_text[:MAX_TELEGRAM_MESSAGE_LEN - 10] + "\n…"

        return card_text
