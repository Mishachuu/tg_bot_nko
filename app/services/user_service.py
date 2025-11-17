from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_app import AppUser
from app.repositories.user_repository import UserRepository
from typing import List, Optional

class UserService:
    def __init__(self, repo_user: UserRepository):
        self.repo_user = repo_user

    async def get_user_profile(self, session: AsyncSession, tg_id) -> AppUser:
        user = await self.repo_user.get_by_tgId(session, tg_id)
        return user
    
    async def check_user(self, session: AsyncSession, tg_id: int):
        result = await self.repo_user.get_by_tgId(session, tg_id)
        if result is None:
            return False
        return True
    
    async def create_user(self, 
                        session: AsyncSession, 
                        tg_id: int, 
                        name: str,
                        email: str = None,
                        phone_number: str = None 
                        ):
        user = AppUser(
            tg_id=tg_id,
            name=name,
            email=email,
            phone_number=phone_number
        )
        return await self.repo_user.add_user(session, user)

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> Optional[AppUser]:
        return await self.repo_user.get_by_id(session, user_id)

    async def list_users(self, session: AsyncSession, skip: int = 0, limit: int = 100, is_lessor: Optional[bool] = None) -> List[AppUser]:
        """Получить список пользователей с пагинацией и фильтрацией"""
        return await self.repo_user.get_users_paginated(session, skip, limit, is_lessor)

    async def get_total_count(self, session: AsyncSession, is_lessor: Optional[bool] = None) -> int:
        """Получить общее количество пользователей с учетом фильтров"""
        return await self.repo_user.get_total_count(session, is_lessor)

    async def update_user(self,
                         session: AsyncSession,
                         user_id: int,
                         name: Optional[str] = None,
                         email: Optional[str] = None,
                         phone_number: Optional[str] = None,
                         is_lessor: Optional[bool] = None,
                         score: Optional[float] = None
                         ) -> Optional[AppUser]:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone_number is not None:
            update_data["phone_number"] = phone_number
        if is_lessor is not None:
            update_data["is_lessor"] = is_lessor
        if score is not None:
            update_data["score"] = score

        if not update_data:
            return None

        return await self.repo_user.update(session, user_id, update_data)

    async def delete_user(self, session: AsyncSession, user_id: int) -> bool:
        return await self.repo_user.delete_by_id(session, user_id)

    async def search_users_by_name(self, session: AsyncSession, name_query: str) -> List[AppUser]:
        return await self.repo_user.search_users_by_name(session, name_query)

    async def get_users_by_lessor_status(self, session: AsyncSession, is_lessor: bool) -> List[AppUser]:
        return await self.repo_user.get_users_by_lessor_status(session, is_lessor)

    async def update_user_score(self, session: AsyncSession, user_id: int, score: float) -> Optional[AppUser]:
        return await self.repo_user.update_user_score(session, user_id, score)

    async def set_lessor_status(self, session: AsyncSession, user_id: int, is_lessor: bool) -> Optional[AppUser]:
        return await self.repo_user.set_lessor_status(session, user_id, is_lessor)

    async def create_user_with_lessor_status(self,
                                           session: AsyncSession,
                                           tg_id: int,
                                           name: str,
                                           is_lessor: bool = False,
                                           email: str = None,
                                           phone_number: str = None,
                                           score: float = 0.0
                                           ) -> AppUser:
        user = AppUser(
            tg_id=tg_id,
            name=name,
            email=email,
            phone_number=phone_number,
            is_lessor=is_lessor,
            score=score
        )
        return await self.repo_user.add_user(session, user, is_lessor=is_lessor)