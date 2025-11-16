# app/api/routes/equipment_photos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db, get_equipment_photo_service
from app.api.schemas.equipment_photo_schema import (
    EquipmentPhotoResponse,
    EquipmentPhotoWithContentResponse,
    EquipmentPhotoCreate,
    EquipmentPhotoListResponse
)
from app.services.equipment_photo_service import EquipmentPhotoService

router = APIRouter(prefix="/equipment-photos", tags=["equipment-photos"])

@router.get("/equipment/{equipment_id}", response_model=EquipmentPhotoListResponse)
async def get_photos_by_equipment_id(
    equipment_id: int,
    session: AsyncSession = Depends(get_db),
    photo_service: EquipmentPhotoService = Depends(get_equipment_photo_service)
):
    """Получить все фото для оборудования по ID оборудования"""
    photos = await photo_service.get_photos_by_equipment_id(session, equipment_id)
    
    # Преобразуем в словари, если нужно
    photos_dicts = [photo.to_dict() if hasattr(photo, 'to_dict') else {
        'id': photo.id,
        'equipment_id': photo.equipment_id,
        'filename': photo.filename
    } for photo in photos]
    
    return {
        "photos": photos_dicts,
        "total": len(photos_dicts),
        "equipment_id": equipment_id
    }

@router.get("/{photo_id}", response_model=EquipmentPhotoWithContentResponse)
async def get_photo_by_id(
    photo_id: int,
    session: AsyncSession = Depends(get_db),
    photo_service: EquipmentPhotoService = Depends(get_equipment_photo_service)
):
    """Получить конкретное фото по ID фото"""
    # Вам нужно добавить метод в репозиторий и сервис для получения фото по ID
    photos = await photo_service.list_photos(session, equipment_id=None)  # временное решение
    photo = next((p for p in photos if p.id == photo_id), None)
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return photo

@router.post("/", response_model=EquipmentPhotoResponse)
async def add_equipment_photo(
    photo_data: EquipmentPhotoCreate,
    session: AsyncSession = Depends(get_db),
    photo_service: EquipmentPhotoService = Depends(get_equipment_photo_service)
):
    """Добавить новое фото для оборудования"""
    new_photo_id = await photo_service.add_photo(
        session,
        photo_data.equipment_id,
        photo_data.filename,
        photo_data.content
    )
    
    # Получаем созданное фото для ответа
    photos = await photo_service.list_photos(session, photo_data.equipment_id)
    new_photo = next((p for p in photos if p.id == new_photo_id), None)
    
    if not new_photo:
        raise HTTPException(status_code=500, detail="Failed to create photo")
    
    return new_photo

@router.delete("/{photo_id}")
async def delete_equipment_photo(
    photo_id: int,
    session: AsyncSession = Depends(get_db),
    photo_service: EquipmentPhotoService = Depends(get_equipment_photo_service)
):
    """Удалить фото оборудования"""
    deleted = await photo_service.delete_photo(session, photo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return {"message": "Photo deleted successfully"}