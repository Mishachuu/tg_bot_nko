import asyncio
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models import equipment, user_app, category, booking, review  # импорт всех моделей
from app.services.set_mockup_service import SetMockupService
from sqlalchemy import text

async def create_tables():
    """Создает все таблицы в базе данных"""
    try:
        print("🗄️ Создание таблиц в базе данных...")
        
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Таблицы успешно созданы")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

async def seed_mockup_data(booking_repo, repo_equipment, repo_user, repo_category):
    """Загрузка тестовых данных с правильным порядком параметров"""
    async with AsyncSessionLocal() as session:
        # ПРАВИЛЬНЫЙ ПОРЯДОК: user_repo, equipment_repo, category_repo, booking_repo
        mockup_service = SetMockupService(
            user_repo=repo_user,           # первый параметр - user_repo
            equipment_repo=repo_equipment, # второй - equipment_repo  
            category_repo=repo_category,   # третий - category_repo
            booking_repo=booking_repo      # четвертый - booking_repo
        )
        
        await mockup_service.set_mockup()

async def db_init_main(booking_repo, repo_equipment, repo_user, repo_category, MOCKUP_REQUIRED):
    """Инициализация базы данных с обработкой ошибок"""
    try:
        # 1. Сначала создаем таблицы
        await create_tables()
        
        # 2. Затем загружаем тестовые данные (если нужно)
        if MOCKUP_REQUIRED and MOCKUP_REQUIRED.lower() == 'true':
            print("📦 Загрузка тестовых данных...")
            
            try:
                await seed_mockup_data(booking_repo, repo_equipment, repo_user, repo_category)
                print("✅ Тестовые данные успешно загружены")
                
                # 3. Обновляем sequences после загрузки данных
                async with AsyncSessionLocal() as session:
                    await update_sequences(session)
                    
            except Exception as e:
                print(f"⚠️ Не удалось загрузить тестовые данные: {e}")
                # Продолжаем работу даже если мокап не загрузился
                    
        else:
            print("ℹ️ Загрузка тестовых данных отключена")
                
    except Exception as e:
        print(f"💥 Ошибка при инициализации БД: {e}")
        raise

async def update_sequences(session):
    """Обновляет sequences для всех таблиц после загрузки мокап данных"""
    try:
        print("🔄 Обновление sequences...")
        
        tables = ['users', 'equipments', 'categories', 'bookings', 'reviews']
        
        for table in tables:
            # Проверяем есть ли записи в таблице
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            
            if count > 0:
                # Если есть записи, обновляем sequence
                await session.execute(
                    text(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM {table}))")
                )
                print(f"✅ Sequence для {table} обновлен")
            else:
                # Если таблица пустая, сбрасываем sequence в 1
                await session.execute(text(f"SELECT setval('{table}_id_seq', 1, false)"))
                print(f"✅ Sequence для {table} сброшен")
        
        await session.commit()
        print("✅ Все sequences обновлены")
        
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении sequences: {e}")
        await session.rollback()