#from app.repositories.city_repository import CityRepository
from sqlalchemy.ext.asyncio import AsyncSession


class CityService:
    def __init__(self, repo=None):
        self._repo = repo
    
    async def get_name_city_by_id(self, session, city_id):
        return "Самара"