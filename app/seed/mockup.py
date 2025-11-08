from datetime import datetime
from pathlib import Path
from app.models.equipment import Equipment
from app.models.user_app import AppUser


BASE_DIR = Path(__file__).parent
PLUG_PATH = BASE_DIR / "plug.jpg"

with open(PLUG_PATH, "rb") as f:
    PLUG_BYTES = f.read()


# ---------- Владельцы ----------
USERS = [
    AppUser(
        id=1,
        name="Петр",
        tg_id=1,
        phone_number="+79383716517",
        email="petr@gmail.com",
        is_lessor=True,
        city_id=2,
        score=5,
    ),
    AppUser(
        id=2,
        name="Василий",
        tg_id=2,  # был дубликат 1 — сделал уникальным
        phone_number="+79383316517",
        email="vasily@gmail.com",
        is_lessor=True,
        city_id=1,
        score=4.9,
    ),
    AppUser(
        id=3,
        name="Иван",
        tg_id=3,
        phone_number="+79383316517",
        email="Ivan@gmail.com",
        is_lessor=False,
        city_id=1,
        score=4.9,
    ),
    AppUser(
        id=4,
        name="Игнат",
        tg_id=4,
        phone_number="+79383316517",
        email="Ignat@gmail.com",
        is_lessor=False,
        city_id=2,
        score=4.9,
    ),
    AppUser(
        id=5,
        name="Матвей",
        tg_id=789235294,
        phone_number="+79093316515",
        email="matvey@gmail.com",
        is_lessor=True,
        city_id=1,
        score=1,
    ),
]


# ---------- Категории ----------
CATEGORIES = [
    {"id": 1, "name": "звук", "is_accepted": True},
    {"id": 2, "name": "свет", "is_accepted": True},
    {"id": 3, "name": "мебель", "is_accepted": True},
    {"id": 4, "name": "техника", "is_accepted": False},  # раньше был дубликат id=3
]

# ---------- Оборудование ----------
MOCK_EQUIPMENT = [
    Equipment(
        id=1,
        name="Микшер Yamaha MG10XU",
        city_id=1,
        user_id=USERS[0].id,
        category_id=CATEGORIES[0]["id"],
        is_approved=True,
        description="10-канальный аналоговый микшер с эффектами.",
        quantity=1,
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        latitude=55.7558,  # Москва
        longitude=37.6173,
    ),
    Equipment(
        id=2,
        name="Сабвуфер JBL PRX818XLF",
        city_id=1,
        user_id=USERS[0].id,
        category_id=CATEGORIES[0]["id"],
        is_approved=False,
        description='18" активный сабвуфер.',
        quantity=2,
        created_at=datetime(2025, 1, 2, 12, 0, 0),
        latitude=53.195,  # Самара
        longitude=50.100,
    ),
    Equipment(
        id=3,
        name="Светодиодный прожектор Chauvet DJ SlimPAR 56",
        city_id=2,
        user_id=USERS[1].id,
        category_id=CATEGORIES[1]["id"],
        is_approved=True,
        description="Компактный RGB прожектор, DMX.",
        quantity=8,
        created_at=datetime(2025, 1, 3, 12, 0, 0),
        latitude=55.7558,  # Москва
        longitude=37.6173,
    ),
    Equipment(
        id=4,
        name="Стойка для микрофона K&M 210/9",
        city_id=1,
        user_id=USERS[1].id,
        category_id=CATEGORIES[2]["id"],
        is_approved=True,
        description="Телескопическая стойка, классика сцены.",
        quantity=6,
        created_at=datetime(2025, 1, 4, 12, 0, 0),
        latitude=53.195,  # Самара
        longitude=50.100,
    ),
    Equipment(
        id=5,
        name="LED панель Godox LEDP120C",
        city_id=2,
        user_id=USERS[1].id,
        category_id=CATEGORIES[1]["id"],
        is_approved=False,
        description="Биколор панель для интервью.",
        quantity=3,
        created_at=datetime(2025, 1, 5, 12, 0, 0),
        latitude=55.7558,  # Москва
        longitude=37.6173,
    ),
    Equipment(
        id=6,
        name="Стул складной Икеа",
        city_id=1,
        user_id=USERS[2].id,
        category_id=CATEGORIES[2]["id"],
        is_approved=True,
        description="Простой складной стул для зрителей.",
        quantity=40,
        created_at=datetime(2025, 1, 6, 12, 0, 0),
        latitude=53.195,  # Самара
        longitude=50.100,
    ),
    Equipment(
        id=7,
        name="DMX Controller 192",
        city_id=2,
        user_id=USERS[2].id,
        category_id=CATEGORIES[1]["id"],
        is_approved=False,
        description="Базовый контроллер на 192 канала.",
        quantity=1,
        created_at=datetime(2025, 1, 7, 12, 0, 0),
        latitude=55.7558,  # Москва
        longitude=37.6173,
    ),
    Equipment(
        id=8,
        name="RCF ART 712-A (активная колонка)",
        city_id=1,
        user_id=USERS[3].id,
        category_id=CATEGORIES[0]["id"],
        is_approved=True,
        description='700W, 12" драйвер, ровный звук.',
        quantity=2,
        created_at=datetime(2025, 1, 8, 12, 0, 0),
        latitude=53.195,  # Самара
        longitude=50.100,
    ),
    Equipment(
        id=9,
        name="Диван двухместный",
        city_id=2,
        user_id=USERS[4].id,
        category_id=CATEGORIES[2]["id"],
        is_approved=False,
        description="Комфорт для лаунж-зоны или гримёрки.",
        quantity=1,
        created_at=datetime(2025, 1, 9, 12, 0, 0),
        latitude=55.7558,  # Москва
        longitude=37.6173,
    ),
    Equipment(
        id=10,
        name="Световая стойка с диммером",
        city_id=1,
        user_id=USERS[4].id,
        category_id=CATEGORIES[1]["id"],
        is_approved=True,
        description="Стойка + диммерный блок на 4 канала.",
        quantity=2,
        created_at=datetime(2025, 1, 10, 12, 0, 0),
        latitude=53.195,  # Самара
        longitude=50.100,
    ),
]

# ---------- Фото оборудования ----------
MOCK_EQUIPMENT_PHOTOS = [
    {"id": 1, "equipment_id": 1, "filename": "plug.png", "content": PLUG_BYTES}
]

# ---------- Бронирования ----------
MOCK_BOOKINGS = [
    {
        "id": 1,
        "equipment_id": 2,  # Сабвуфер JBL
        "user_id": 3,       # Дмитрий
        "date_from": datetime(2025, 2, 10),
        "date_to": datetime(2025, 2, 12),
    },
    {
        "id": 2,
        "equipment_id": 8,  # Колонки RCF ART
        "user_id": 4,       # Мария
        "date_from": datetime(2025, 3, 5),
        "date_to": datetime(2025, 3, 8),
    },
    {
        "id": 3,
        "equipment_id": 5,  # LED панель
        "user_id": 2,       # Анна
        "date_from": datetime(2025, 1, 20),
        "date_to": datetime(2025, 1, 22),
    },
]

MOCK_CITY = [
    {"id": 1, "name": "Самара"},
    {"id": 2, "name": "Москва"},
]
