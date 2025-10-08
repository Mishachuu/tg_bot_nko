import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.equipment import Equipment, RentalStatus
from app.repositories.equipment_repository import EquipmentRepository

class MockDataGenerator:
    """Генератор моковых данных для демонстрации"""
    
    @staticmethod
    async def create_mock_data(session: AsyncSession, equipment_repository: EquipmentRepository):
        """Создает демонстрационные данные"""
        
        # Оборудование для текущего пользователя (user_id = 1)
        my_equipment = [
            Equipment(
                id=1,
                name="Профессиональный микшерный пульт",
                description="Yamaha MG16XU, 16 каналов, USB интерфейс",
                quantity=1,
                city_id=1,
                category_id=1,
                status=RentalStatus.AVAILABLE,
                landlord_id=1,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=10)
            ),
            Equipment(
                id=2,
                name="Сценические мониторы",
                description="JBL EON612, 1000Вт, отличное состояние",
                quantity=4,
                city_id=1,
                category_id=1,
                status=RentalStatus.BOOKED,
                landlord_id=1,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=5)
            ),
            Equipment(
                id=3,
                name="LED-прожекторы",
                description="RGB прожекторы 50Вт, пульт ДУ",
                quantity=8,
                city_id=1,
                category_id=2,
                status=RentalStatus.AVAILABLE,
                landlord_id=1,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=3)
            ),
            Equipment(
                id=4,
                name="Складные столы",
                description="Столы 180x80см, алюминиевая рама",
                quantity=6,
                city_id=1,
                category_id=3,
                status=RentalStatus.IN_USE,
                landlord_id=1,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=1)
            ),
            Equipment(
                id=5,
                name="Цифровая видеокамера",
                description="Sony PXW-Z90, 4K HDR",
                quantity=1,
                city_id=1,
                category_id=4,
                status=RentalStatus.AVAILABLE,
                landlord_id=1,
                is_approved=False,
                created_at=datetime.now()
            )
        ]
        
        # Оборудование других пользователей
        other_equipment = [
            Equipment(
                id=6,
                name="Бас-гитарный усилитель",
                description="Ampeg SVT-4 PRO, 1200Вт",
                quantity=1,
                city_id=2,
                category_id=1,
                status=RentalStatus.AVAILABLE,
                landlord_id=2,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=15)
            ),
            Equipment(
                id=7,
                name="Лазерный проектор",
                description="KVANT Clubmax 3000, зеленый лазер",
                quantity=1,
                city_id=3,
                category_id=2,
                status=RentalStatus.AVAILABLE,
                landlord_id=3,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=8)
            ),
            Equipment(
                id=8,
                name="Сценический генератор тумана",
                description="Look Unique Tour Hazer, дистанционное управление",
                quantity=2,
                city_id=1,
                category_id=2,
                status=RentalStatus.AVAILABLE,
                landlord_id=4,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=12)
            ),
            Equipment(
                id=9,
                name="Пауэрбанки переносные",
                description="Jackery Explorer 500, 518Втч",
                quantity=3,
                city_id=4,
                category_id=5,
                status=RentalStatus.AVAILABLE,
                landlord_id=5,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=6)
            ),
            Equipment(
                id=10,
                name="Трибуны для зрителей",
                description="Мобильные трибуны, секция на 10 человек",
                quantity=5,
                city_id=5,
                category_id=3,
                status=RentalStatus.AVAILABLE,
                landlord_id=6,
                is_approved=True,
                created_at=datetime.now() - timedelta(days=20)
            )
        ]
        
        # В реальном приложении здесь был бы код сохранения в БД
        # Для демо просто возвращаем данные
        return my_equipment + other_equipment