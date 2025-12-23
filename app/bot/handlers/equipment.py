from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
from app.db.session import AsyncSessionLocal
from app.models.equipment import Equipment
from datetime import datetime


class EquipmentHandler:
    def __init__(self, user_service, equipment_service, equipment_photo_service, category_service, formatter):
        self.user_service = user_service
        self.equipment_service = equipment_service
        self.equipment_photo_service = equipment_photo_service
        self.category_service = category_service
        self.formatter = formatter

    async def check_lessor_and_start(self, update, user_states, user_id):
        async with AsyncSessionLocal() as session:
            user = await self.user_service.get_user_profile(session, user_id)

        if not user.is_lessor:
            await update.message.reply_text(
                "❌ У вас нет прав на добавление оборудования. Обратитесь к администратору."
            )
            return

        user_states[user_id] = {"state": "add_equipment_name", "data": {}}
        await update.message.reply_text(
            "📝 Введите название оборудования:", reply_markup=ReplyKeyboardRemove()
        )

