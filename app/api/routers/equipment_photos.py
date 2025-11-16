# app/api/routes/equipment_photos.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db, get_equipment_photo_service
from app.api.schemas.equipment_photo_schema import (
    EquipmentPhotoResponse,
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
    
    # Исключаем content из ответа
    photos_without_content = []
    for photo in photos:
        photo_dict = {
            "id": photo["id"],
            "equipment_id": photo["equipment_id"],
            "filename": photo["filename"]
        }
        photos_without_content.append(photo_dict)
    
    return {
        "photos": photos_without_content,
        "total": len(photos_without_content),
        "equipment_id": equipment_id
    }

@router.get("/{photo_id}/image")
async def get_photo_image(
    photo_id: int,
    session: AsyncSession = Depends(get_db),
    photo_service: EquipmentPhotoService = Depends(get_equipment_photo_service)
):
    """Получить изображение как файл"""
    photo = await photo_service.get_photo_by_id(session, photo_id)
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Определяем content-type по расширению файла
    filename = photo['filename'].lower()
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        media_type = "image/jpeg"
    elif filename.endswith('.png'):
        media_type = "image/png"
    elif filename.endswith('.gif'):
        media_type = "image/gif"
    else:
        media_type = "application/octet-stream"
    
    return Response(
        content=photo['content'],
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename={photo['filename']}"}
    )

# Удалите старый эндпоинт get_photo_by_id или закомментируйте его
# @router.get("/{photo_id}", response_model=EquipmentPhotoWithContentResponse)
# async def get_photo_by_id(...):

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
    new_photo = next((p for p in photos if p["id"] == new_photo_id), None)
    
    if not new_photo:
        raise HTTPException(status_code=500, detail="Failed to create photo")
    
    # Исключаем content из ответа
    return {
        "id": new_photo["id"],
        "equipment_id": new_photo["equipment_id"],
        "filename": new_photo["filename"]
    }

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