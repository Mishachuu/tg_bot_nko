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