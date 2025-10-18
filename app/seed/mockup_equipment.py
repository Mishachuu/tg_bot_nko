from datetime import datetime, timedelta
from app.models.equipment import Equipment, RentalStatus

async def create_mock_data() -> list[Equipment]:
    """Создает демонстрационные данные"""
    
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
    ]
    
    other_equipment = [
        Equipment(
            id=4,
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
            id=5,
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
    ]
    
    return my_equipment + other_equipment