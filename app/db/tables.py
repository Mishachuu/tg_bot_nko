from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime, MetaData, DateTime, ForeignKey, LargeBinary
)

metadata = MetaData()

category_table = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False, unique=True),
)

equipment_table = Table(
    "equipment",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=True),
    Column("city_id", Integer, nullable=True),
    Column("landlord_id", Integer, nullable=True),
    Column("status", String, nullable=False),
    Column("photo", String, nullable=True),
    Column("category_id", Integer, nullable=True),
    Column("is_approved", Boolean, nullable=False, default=False),
    Column("description", String, nullable=True),
    Column("quantity", Integer, nullable=False, default=1),
    Column("created_at", DateTime, nullable=True),
)

equipment_photos_table = Table(
    "equipment_photos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False),
    Column("filename", String, nullable=True),   # оригинальное имя файла
    Column("content", LargeBinary, nullable=False),  # бинарное содержимое
)

bookings_table = Table(
    "bookings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id"), nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime, nullable=False),
)