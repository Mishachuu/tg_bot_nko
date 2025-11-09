from sqlalchemy import (Table, Column, Integer, String, Boolean, DateTime, MetaData, DateTime, ForeignKey, LargeBinary, Float)
from app.db.base import metadata

# описание Доп таблиц

category_table = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False, unique=True),
    Column("is_accepted", Boolean)
)

bookings_table = Table(
    "bookings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_id", Integer, ForeignKey("equipments.id"), nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False), # id пользователя который забронировал 
    Column("date_from", DateTime, nullable=False),
    Column("date_to", DateTime, nullable=False),
)
city_table = Table(
    "cities",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False, unique=True)
)
reviews_table = Table(
    "reviews",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("equipment_id", Integer, ForeignKey("equipments.id"), nullable=False),
    Column("renter_id", Integer, ForeignKey("users.id"), nullable=False),   # кто арендовал
    Column("owner_id", Integer, ForeignKey("users.id"), nullable=False),    # владелец
    Column("rating", Integer, nullable=False),                              # 1..5
    Column("comment", String, nullable=True),
    Column("created_at", DateTime, nullable=False),
)