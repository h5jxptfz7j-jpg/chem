from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("")
async def get_profile(
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(User).where(User.telegram_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"detail": "User not found"}
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "photo_url": user.photo_url,
        "display_name": user.username or f"{user.first_name or ''} {user.last_name or ''}".strip() or f"User {user.telegram_id}"
    }