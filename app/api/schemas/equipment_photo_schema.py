# app/api/schemas/equipment_photo_schema.py
from pydantic import BaseModel, ConfigDict
from typing import List

class EquipmentPhotoResponse(BaseModel):
    id: int
    equipment_id: int
    filename: str
    
    model_config = ConfigDict(from_attributes=True)

# Уберите EquipmentPhotoWithContentResponse или закомментируйте
# class EquipmentPhotoWithContentResponse(BaseModel):
#     id: int
#     equipment_id: int
#     filename: str
#     content: bytes
#     
#     model_config = ConfigDict(from_attributes=True)

class EquipmentPhotoCreate(BaseModel):
    equipment_id: int
    filename: str
    content: bytes

class EquipmentPhotoListResponse(BaseModel):
    photos: List[EquipmentPhotoResponse]
    total: int
    equipment_id: int