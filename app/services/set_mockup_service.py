# app/services/equipment_service.py
from __future__ import annotations
from typing import List, Optional

from typing import Iterable
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment
from app.models.user_app import AppUser

from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.repositories.city_repository import CityRepository
from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
from app.seed.mockup import *



class SetMockupService:
    """
    Сервисный слой: инкапсулирует бизнес-логику и транзакционные решения.
    Этим слоем пользуются боты и будущий сайт — он не знает SQL и таблиц.
    """

    def __init__(self, 
                 equipment_repo: EquipmentRepository, 
                 booking_repo: BookingRepository,
                 category_repo: CategoryRepository,
                 user_repo: UserRepository,
                 city_repo: CityRepository,
                 #equipment_photo_repo: EquipmentPhotoRepository
                 ):
        self.equipment_repo = equipment_repo
        self.booking_repo = booking_repo
        self.category_repo = category_repo
        self.user_repo = user_repo
        self.city_repo = city_repo
        #self.equipment_photo_repo = equipment_photo_repo


    async def create_users(self, session):
        for user in USERS:
            await self.user_repo.add_user(session, user)

    async def create_booking(self, session):
        for booking in MOCK_BOOKINGS:
            await self.booking_repo.add_booking(session, booking)
        await session.commit()

    async def create_equipments(self, session):
        for equipment in MOCK_EQUIPMENT:
            await self.equipment_repo.add_equipment(session, equipment)
        await session.commit()

    async def create_categories(self, session):
        for cat in CATEGORIES:
            await self.category_repo.add_category(session, cat)  # см. правку репозитория ниже
        await session.commit()

    async def create_city(self, session):
        for city in MOCK_CITY:
            await self.city_repo.add_city(session, city["name"]) # repo ждёт name
        await session.commit()

    async def create_photos(self, session):
        pass

    # create_all_tables можно не использовать; если хочешь — не забудь await перед каждым вызовом
    
    async def create_all_tables(self, session: AsyncSession):
        self.create_users(session)
        self.create_booking(session)
        self.create_equipments(session)
        self.create_categories(session)
        self.create_city(session)
            
                


