from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime, MetaData, DateTime, ForeignKey, LargeBinary, Float
)

metadata = MetaData()


user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False, unique=True),
    Column("tg_id", Integer, nullable=False, unique=True),
    Column("phone_number", String, nullable=True, unique=True),
    Column("email", String, nullable=True, unique=True),
    Column("allow_pub", Boolean, nullable=True),
    Column("city", String, nullable=True),
    Column("score", Float, default=0),
)

category_table = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False, unique=True),
    Column("is_accepted", Boolean)
)

equipment_table = Table(
    "equipment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=True),
    Column("city_id", Integer, nullable=True),
    Column("user_id", Integer, ForeignKey("users.id") , nullable=True),
    Column("status", String, nullable=False),
    Column("category_id", Integer, nullable=True),
    Column("is_approved", Boolean, nullable=False),
    Column("description", String, nullable=True),
    Column("quantity", Integer, nullable=False, default=1),
    Column("created_at", DateTime, nullable=True),
    Column("latitude", Float, nullable=True),
    Column("longitude", Float, nullable=True),
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
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False), # id пользователя который забронировал 
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime, nullable=False),
)