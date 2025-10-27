import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.config import setting

#DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/dbname")

engine = create_async_engine(
    url= setting.DATABASE_URL_asyncpg, 
    echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
