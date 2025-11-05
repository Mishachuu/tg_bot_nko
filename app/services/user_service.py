from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_app import AppUser
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo_user: UserRepository):
        self.repo_user = repo_user

    async def get_user_profile(self, session:AsyncSession, tg_id):
        user = await self.repo_user.get_by_tgId(session, tg_id)
        return user
    async def check_user(self, session: AsyncSession, tg_id: int):
        """Проверяем существует ли пользователь в БД или мы должны его зарегестровать
            Return: 
                True - пользователь найден и регистрация не требуется 
                Fasle - пользлваьтель не найден => пользовтеля нужно зарегать 
        """
        result = await self.repo_user.get_by_tgId(session, tg_id)
        if(result == None):
            return False
        return True
    async def create_user(self, 
                        session: AsyncSession, 
                        tg_id: int, 
                        name: str,
                        city_id: int = None,
                        email: str = None,
                        phone_number: str = None 
                        ):
        user = AppUser(
                    tg_id=tg_id,
                    name=name,
                    city_id=city_id,
                    email=email,
                    phone_number=phone_number)
        return await self.repo_user.post(session, user)
