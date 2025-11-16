from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.equipment_photo import EquipmentPhoto
from typing import Optional

class EquipmentPhotoRepository:
    def __init__(self):
        self.model = EquipmentPhoto

    async def add_photo(self, session: AsyncSession, equipment_id: int, filename: str, content: bytes) -> int:
        """Добавляет фото оборудования"""
        photo = EquipmentPhoto(
            equipment_id=equipment_id,
            filename=filename,
            content=content
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        return photo.id
    
    async def get_photo_by_id(self, session: AsyncSession, photo_id: int) -> Optional[EquipmentPhoto]:
        """Получает фото по ID"""
        stmt = select(self.model).where(self.model.id == photo_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_photos_by_equipment(self, session: AsyncSession, equipment_id: int) -> list[dict]:
        """Получает все фото оборудования"""
        stmt = select(self.model).where(self.model.equipment_id == equipment_id)
        result = await session.execute(stmt)
        photos = result.scalars().all()
        return [photo.to_dict() for photo in photos]

    async def delete_photo(self, session: AsyncSession, photo_id: int) -> bool:
        """Удаляет фото по ID"""
        stmt = select(self.model).where(self.model.id == photo_id)
        result = await session.execute(stmt)
        photo = result.scalar_one_or_none()
        
        if photo:
            await session.delete(photo)
            await session.commit()
            return True
        return False