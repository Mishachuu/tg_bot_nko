from app.models.user_app import AppUser
from typing import Optional, Tuple


async def get_owner_info(user_service, context, owner_id: int) -> Tuple[str, Optional[int], Optional[str]]:
    """Return (owner_info_str, owner_tg_id, owner_username)"""
    owner: AppUser = await user_service.get_user_by_id(None, owner_id)
    owner_info = " (владелец не указан)"
    owner_tg_id = None
    owner_username = None

    if owner and owner.tg_id:
        owner_tg_id = owner.tg_id
        try:
            tguser = await context.bot.get_chat(owner.tg_id)
            username = tguser.username
            owner_username = username
            owner_info = f" @{username}" if username else " (username не указан)"
        except Exception:
            owner_info = " (профиль недоступен)"

    return owner_info, owner_tg_id, owner_username


async def get_category_name(category_service, session, category_id: int) -> str:
    if not category_id:
        return "Не указано"
    try:
        category = await category_service.get_by_id(session, category_id)
        return category.name if category else "Неизвестная категория"
    except Exception:
        return "Неизвестная категория"

