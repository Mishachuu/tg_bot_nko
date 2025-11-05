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


    async def create_users(self, session: AsyncSession):
        for user in USERS:
            self.user_repo.add_user(session, user)
    
    async def create_booking(self, session: AsyncSession):
        for booking in MOCK_BOOKINGS:
            self.booking_repo.add_booking(session, booking)

    async def create_equipments(self, session: AsyncSession):
        for equipmen in MOCK_EQUIPMENT:
            self.equipment_repo.add_equipment(session, equipmen)

    async def create_categories(self, session: AsyncSession):
        for category in CATEGORIES:
            self.category_repo.add_category(session, category)

    async def create_city(self, session: AsyncSession):
        for city in MOCK_CITY:
            self.city_repo.add_city(session, city)

    async def create_photos(self, session: AsyncSession):
        pass
    
    async def create_all_tables(self, session: AsyncSession):
        self.create_users(session)
        self.create_booking(session)
        self.create_equipments(session)
        self.create_categories(session)
        self.create_city(session)
            
                


