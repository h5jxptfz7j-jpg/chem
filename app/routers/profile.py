import json
from urllib.parse import unquote, parse_qs
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return {"detail": "User not found"}

    return {
        "telegram_id": user.telegram_id,
        "username":    user.username,
        "first_name":  user.first_name,
        "last_name":   user.last_name,
        "photo_url":   user.photo_url,
        "display_name": (
            user.username
            or f"{user.first_name or ''} {user.last_name or ''}".strip()
            or f"User {user.telegram_id}"
        ),
    }


@router.get("/debug-init")
async def debug_init(request: Request):
    auth = request.headers.get("Authorization", "")
    init_data = auth[len("Bearer "):] if auth.startswith("Bearer ") else ""

    raw = unquote(init_data)[:500]

    user_obj = None
    try:
        parsed = parse_qs(raw)
        user_str = parsed.get("user", [None])[0]
        if user_str:
            user_obj = json.loads(user_str)
    except Exception as e:
        user_obj = {"error": str(e)}

    return {
        "raw_init_data": raw,
        "parsed_user": user_obj,
    }
