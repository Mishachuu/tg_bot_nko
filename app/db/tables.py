from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime, MetaData
)
from sqlalchemy import ForeignKey

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
