from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.dependencies import get_db, get_equipment_service
from app.api.schemas.equipment import (
    EquipmentCreate, EquipmentResponse, EquipmentUpdate,
    EquipmentApprovalUpdate, EquipmentPublishUpdate, EquipmentQuantityUpdate,
    EquipmentListResponse, EquipmentDetailedResponse, EquipmentSearchParams
)
from app.services.equipment_service import EquipmentService

router = APIRouter(prefix="/equipment", tags=["equipment"])

# БАЗОВЫЕ CRUD ОПЕРАЦИИ
@router.post("/", response_model=EquipmentResponse)
async def create_equipment(
    equipment_data: EquipmentCreate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Создать новое оборудование"""
    equipment = await equipment_service.create_equipment_from_params(
        session,
        equipment_data.name,
        equipment_data.user_id,
        equipment_data.category_id,
        equipment_data.description,
        equipment_data.quantity,
        equipment_data.latitude,
        equipment_data.longitude
    )
    return equipment

@router.get("/", response_model=EquipmentListResponse)
async def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить список оборудования с пагинацией"""
    equipments = await equipment_service.list_equipment(session, limit=limit, offset=skip)
    total_count = await equipment_service.get_total_count(session)
    return {
        "equipments": equipments,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

@router.get("/{equipment_id}", response_model=EquipmentDetailedResponse)
async def get_equipment(
    equipment_id: int,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить оборудование по ID"""
    equipment = await equipment_service.get_equipment(session, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.put("/{equipment_id}", response_model=EquipmentDetailedResponse)
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Обновить данные оборудования"""
    equipment = await equipment_service.update_equipment(
        session,
        equipment_id,
        **equipment_data.model_dump(exclude_unset=True)
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: int,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Удалить оборудование"""
    success = await equipment_service.delete_equipment(session, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}

# СПЕЦИАЛЬНЫЕ ОПЕРАЦИИ
@router.patch("/{equipment_id}/approval", response_model=EquipmentDetailedResponse)
async def update_equipment_approval(
    equipment_id: int,
    approval_data: EquipmentApprovalUpdate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Обновить статус одобрения оборудования"""
    equipment = await equipment_service.approve_with_status(
        session, 
        equipment_id, 
        approval_data.is_approved
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.patch("/{equipment_id}/publish", response_model=EquipmentDetailedResponse)
async def update_equipment_publish(
    equipment_id: int,
    publish_data: EquipmentPublishUpdate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Обновить статус публикации оборудования"""
    equipment = await equipment_service.set_publish(
        session, 
        equipment_id, 
        publish_data.is_publish
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.patch("/{equipment_id}/quantity", response_model=EquipmentDetailedResponse)
async def update_equipment_quantity(
    equipment_id: int,
    quantity_data: EquipmentQuantityUpdate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Обновить количество оборудования"""
    equipment = await equipment_service.update_equipment(
        session,
        equipment_id,
        quantity=quantity_data.quantity
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

# ПОИСК И ФИЛЬТРАЦИЯ
@router.get("/user/{user_id}", response_model=List[EquipmentResponse])
async def get_equipment_by_owner(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить оборудование по владельцу"""
    equipments = await equipment_service.list_by_owner(session, user_id)
    return equipments

@router.get("/category/{category_id}", response_model=List[EquipmentResponse])
async def get_equipment_by_category(
    category_id: int,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить оборудование по категории"""
    equipments = await equipment_service.find_by_category(session, category_id)
    return equipments

@router.get("/status/approved", response_model=List[EquipmentResponse])
async def get_approved_equipment(
    is_approved: bool = Query(True),
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить оборудование по статусу одобрения"""
    equipments = await equipment_service.get_equipment_by_approval_status(session, is_approved)
    return equipments

@router.get("/status/published", response_model=List[EquipmentResponse])
async def get_published_equipment(
    is_publish: bool = Query(True),
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Получить оборудование по статусу публикации"""
    equipments = await equipment_service.get_equipment_by_publish_status(session, is_publish)
    return equipments

@router.post("/search", response_model=List[EquipmentResponse])
async def search_equipment(
    search_params: EquipmentSearchParams,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Расширенный поиск оборудования"""
    equipments = await equipment_service.search_equipment(
        session,
        category_id=search_params.category_id,
        user_id=search_params.user_id,
        is_approved=search_params.is_approved,
        is_publish=search_params.is_publish,
        name=search_params.name
    )
    return equipments

@router.get("/location/nearby", response_model=List[EquipmentResponse])
async def get_equipment_near_location(
    latitude: float = Query(..., description="Широта"),
    longitude: float = Query(..., description="Долгота"),
    radius_km: float = Query(10, ge=0.1, le=1000, description="Радиус в километрах"),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    """Найти оборудование поблизости"""
    equipments = await equipment_service.find_by_location(
        session,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    return equipments