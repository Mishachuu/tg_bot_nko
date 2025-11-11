from sqlalchemy.ext.asyncio import AsyncSession
from app.models.equipment import Equipment
from app.models.user_app import AppUser
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.seed.mockup import *

class SetMockupService:
    """
    Сервисный слой: инкапсулирует бизнес-логику и транзакционные решения.
    Этим слоем пользуются боты и будущий сайт — он не знает SQL и таблиц.
    """

    def __init__(self, 
                 user_repo: UserRepository,
                 equipment_repo: EquipmentRepository, 
                 category_repo: CategoryRepository,
                 booking_repo: BookingRepository
                 ):
        self.user_repo = user_repo
        self.equipment_repo = equipment_repo
        self.category_repo = category_repo
        self.booking_repo = booking_repo

    async def create_users(self, session: AsyncSession):
        """Создание пользователей с обработкой ошибок"""
        try:
            for user in USERS:
                await self.user_repo.add_user(session, user)
            await session.commit()
            print("✅ Пользователи созданы")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании пользователей: {e}")
            raise

    async def create_categories(self, session: AsyncSession):
        """Создание категорий с обработкой ошибок"""
        try:
            for cat in CATEGORIES:
                await self.category_repo.create(session, cat)
            await session.commit()
            print("✅ Категории созданы")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании категорий: {e}")
            raise

    async def create_equipments(self, session: AsyncSession):
        """Создание оборудования с обработкой ошибок"""
        try:
            for equipment in MOCK_EQUIPMENT:
                await self.equipment_repo.add_equipment(session, equipment)
            await session.commit()
            print("✅ Оборудование создано")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании оборудования: {e}")
            raise

    async def create_bookings(self, session: AsyncSession):
        """Создание бронирований с обработкой ошибок"""
        try:
            for booking in MOCK_BOOKINGS:
                await self.booking_repo.create(session, booking)
            await session.commit()
            print("✅ Бронирования созданы")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании бронирований: {e}")
            raise

    async def create_reviews(self, session: AsyncSession):
        """Создание отзывов с обработкой ошибок"""
        try:
            for review in MOCK_REVIEWS:
                await self.review_repo.create(session, review)
            await session.commit()
            print("✅ Отзывы созданы")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании отзывов: {e}")
            raise

    async def set_mockup(self):
        """Основной метод загрузки всех мокап данных с обработкой ошибок"""
        from app.db.session import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            try:
                print("🚀 Начало загрузки тестовых данных...")
                
                # Создаем данные в правильном порядке (из-за foreign keys)
                await self.create_users(session)
                await self.create_categories(session)
                await self.create_equipments(session)
                await self.create_bookings(session)
                
                print("🎉 Все тестовые данные успешно загружены!")
                
            except Exception as e:
                print(f"💥 Критическая ошибка при загрузке тестовых данных: {e}")
                await session.rollback()
                raise  # Пробрасываем ошибку дальше