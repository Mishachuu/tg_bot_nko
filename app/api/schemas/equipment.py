from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

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
    is_approved: bool
    is_publish: bool
    description: Optional[str]
    quantity: int
    created_at: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_approved: Optional[bool] = None
    is_publish: Optional[bool] = None

class EquipmentApprovalUpdate(BaseModel):
    is_approved: bool

class EquipmentPublishUpdate(BaseModel):
    is_publish: bool

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
    is_approved: Optional[bool] = None
    is_publish: Optional[bool] = None
    name: Optional[str] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 100