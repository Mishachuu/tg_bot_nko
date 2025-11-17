from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.dependencies import get_db, get_equipment_service
from app.api.schemas.equipment import (
    EquipmentListResponse, EquipmentDetailedResponse,
    EquipmentRejectUpdate
)
from app.services.equipment_service import EquipmentService
from app.models.equipment import EquipmentStatus

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.get("/", response_model=EquipmentListResponse)
async def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    equipments = await equipment_service.list_equipment(session, limit=limit, offset=skip)
    total_count = await equipment_service.get_total_count(session)
    return {
        "equipments": equipments,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

# Статусные операции
@router.patch("/{equipment_id}/approve", response_model=EquipmentDetailedResponse)
async def approve_equipment(
    equipment_id: int,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    equipment = await equipment_service.approve_equipment(session, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.patch("/{equipment_id}/reject", response_model=EquipmentDetailedResponse)
async def reject_equipment(
    equipment_id: int,
    reject_data: EquipmentRejectUpdate,
    session: AsyncSession = Depends(get_db),
    equipment_service: EquipmentService = Depends(get_equipment_service)
):
    equipment = await equipment_service.reject_equipment(
        session, 
        equipment_id, 
        reason=reject_data.reason
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment