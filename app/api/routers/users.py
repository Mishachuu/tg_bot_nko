from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db, get_user_service
from app.api.schemas.user_schema import (
    UserCreate, UserResponse, UserCreateWithLessor, 
    UserUpdate, UserScoreUpdate, UserLessorStatusUpdate,
    UserListResponse, UserDetailedResponse
)
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.cli.bot_main import application
router = APIRouter(prefix="/users", tags=["users"])

# СУЩЕСТВУЮЩИЕ ЭНДПОИНТЫ
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.create_user(
        session,
        user_data.tg_id,
        user_data.name,
        user_data.email,
        user_data.phone_number
    )
    return user

@router.get("/telegram/{tg_id}", response_model=UserResponse)
async def get_user_by_telegram(
    tg_id: int,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_profile(session, tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/telegram/{tg_id}/exists")
async def check_user_exists(
    tg_id: int,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    exists = await user_service.check_user(session, tg_id)
    return {"exists": exists}

# НОВЫЕ CRUD ЭНДПОИНТЫ
@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Получить список пользователей с пагинацией"""
    users = await user_service.list_users(session, skip, limit)
    all_users = await user_service.list_users(session, 0, 10000)  # Для подсчета общего количества
    return {
        "users": users,
        "total": len(all_users),
        "skip": skip,
        "limit": limit
    }

@router.get("/{user_id}", response_model=UserDetailedResponse)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Получить пользователя по ID"""
    user = await user_service.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserDetailedResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить данные пользователя"""
    user = await user_service.update_user(
        session,
        user_id,
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        is_lessor=user_data.is_lessor,
        score=user_data.score
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Удалить пользователя"""
    success = await user_service.delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.patch("/{user_id}/score", response_model=UserDetailedResponse)
async def update_user_score(
    user_id: int,
    score_data: UserScoreUpdate,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить рейтинг пользователя"""
    user = await user_service.update_user_score(session, user_id, score_data.score)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}/lessor-status", response_model=UserDetailedResponse)
async def update_lessor_status(
    user_id: int,
    status_data: UserLessorStatusUpdate,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить статус арендодателя"""
    user = await user_service.set_lessor_status(session, user_id, status_data.is_lessor)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if(user.is_lessor):
        text = "🟢Ваш статус Арендатора подтвержден \n\nТеперь Вы можете публиковать оборудования"
    else:
        text = "⚠️Вы были лишены прав Арендатора. \n\nТеперь Вы можете НЕ публиковать оборудования"
    await NotificationService(application).notify_user(user.tg_id,text)
    return user

@router.get("/search/name", response_model=List[UserResponse])
async def search_users_by_name(
    query: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Поиск пользователей по имени"""
    users = await user_service.search_users_by_name(session, query)
    return users

@router.get("/lessor/{is_lessor}", response_model=List[UserResponse])
async def get_users_by_lessor_status(
    is_lessor: bool,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Получить пользователей по статусу арендодателя"""
    users = await user_service.get_users_by_lessor_status(session, is_lessor)
    return users

@router.post("/with-lessor", response_model=UserDetailedResponse)
async def create_user_with_lessor_status(
    user_data: UserCreateWithLessor,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Создать пользователя с указанием статуса арендодателя"""
    user = await user_service.create_user_with_lessor_status(
        session,
        user_data.tg_id,
        user_data.name,
        user_data.is_lessor,
        user_data.email,
        user_data.phone_number,
        user_data.score
    )
    return user