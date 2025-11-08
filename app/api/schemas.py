from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BookingCreate(BaseModel):
    equipment_id: int
    user_id: int
    date_from: datetime
    date_to: datetime


class BookingResponse(BaseModel):
    id: int
    equipment_id: int
    user_id: int
    date_from: datetime
    date_to: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EquipmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    city_id: int
    quantity: int = 1
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class EquipmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    city_id: int
    quantity: int
    is_approved: bool
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    tg_id: int
    name: str
    city_id: Optional[int] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    tg_id: int
    name: str
    city_id: Optional[int]
    email: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class AvailabilityCheck(BaseModel):
    equipment_id: int
    date_from: datetime
    date_to: datetime


class AvailabilityResponse(BaseModel):
    is_available: bool