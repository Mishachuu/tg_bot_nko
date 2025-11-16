from app.repositories.equipment_photo_repository import EquipmentPhotoRepository
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


class EquipmentPhotoService:
    def __init__(self, repo: EquipmentPhotoRepository):
        self._repo = repo

    async def get_photos_by_equipment_id(self, session: AsyncSession, equipment_id: int) -> list[dict]:
        """Получить все фото для оборудования"""
        return await self._repo.get_photos_by_equipment(session, equipment_id)
    
    async def get_photo_by_id(self, session: AsyncSession, photo_id: int) -> Optional[dict]:
        """Получить фото по ID"""
        photo = await self._repo.get_photo_by_id(session, photo_id)
        return photo.to_dict() if photo else None

    async def add_photo(self, session: AsyncSession, equipment_id: int, filename: str, content: bytes) -> int:
        new_id = await self._repo.add_photo(session, equipment_id, filename, content)
        await session.commit()
        return new_id

    async def list_photos(self, session: AsyncSession, equipment_id: int) -> list[dict]:
        return await self._repo.get_photos_by_equipment(session, equipment_id)

    async def delete_photo(self, session: AsyncSession, photo_id: int) -> bool:
        deleted = await self._repo.delete_photo(session, photo_id)
        await session.commit()
        return deleted
