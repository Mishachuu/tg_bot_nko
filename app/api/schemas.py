from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    tg_id: int
    name: str
    city_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    tg_id: int
    name: str
    city_id: Optional[int]
    email: Optional[str]
    phone_number: Optional[str]
    is_lessor: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserCreateWithLessor(BaseModel):
    tg_id: int
    name: str
    is_lessor: bool = False
    city_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    score: float = 0.0

class UserUpdate(BaseModel):
    name: Optional[str] = None
    city_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    is_lessor: Optional[bool] = None
    score: Optional[float] = None

class UserScoreUpdate(BaseModel):
    score: float

class UserLessorStatusUpdate(BaseModel):
    is_lessor: bool

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

class UserDetailedResponse(UserResponse):
    is_lessor: Optional[bool]
    score: float
    
    model_config = ConfigDict(from_attributes=True)