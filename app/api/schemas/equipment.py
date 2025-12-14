from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.equipment import EquipmentStatus  # Импортируем из модели

class EquipmentCreate(BaseModel):
    name: str
    user_id: int
    category_id: int
    description: Optional[str] = None
    quantity: int = 1
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class EquipmentResponse(BaseModel):
    id: int
    name: str
    user_id: int
    category_id: int
    category_name: str
    status: EquipmentStatus
    description: Optional[str]
    quantity: int
    created_at: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    rejection_reason: Optional[str] = None
    moderated_at: Optional[datetime] = None
    moderated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[EquipmentStatus] = None

class EquipmentStatusUpdate(BaseModel):
    status: EquipmentStatus

class EquipmentRejectUpdate(BaseModel):
    reason: Optional[str] = None

class EquipmentQuantityUpdate(BaseModel):
    quantity: int

class EquipmentListResponse(BaseModel):
    equipments: List[EquipmentResponse]
    total: int
    skip: int
    limit: int

class EquipmentDetailedResponse(EquipmentResponse):
    display_status: str
    
    model_config = ConfigDict(from_attributes=True)

class EquipmentSearchParams(BaseModel):
    category_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[EquipmentStatus] = None
    name: Optional[str] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 100

class EquipmentStatsResponse(BaseModel):
    total: int
    moderation: int
    approved: int
    rejected: int