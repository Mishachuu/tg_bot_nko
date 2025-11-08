from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_user_service
from app.api.schemas import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


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
        user_data.city_id,
        user_data.email,
        user_data.phone_number
    )
    await session.commit()
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