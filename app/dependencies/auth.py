import hashlib
import hmac
import time
import json
from urllib.parse import parse_qs, unquote
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import DEV_MODE, BOT_TOKEN, DEV_USER_ID
from app.database import get_session
from app.models.user import User
 
 
def validate_telegram_init_data(init_data: str, token: str) -> dict:
    """Проверяет подпись initData от Telegram и возвращает распарсенные поля."""
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing initData")
 
    parsed = parse_qs(init_data)
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        raise HTTPException(status_code=401, detail="Hash missing from initData")
 
    sorted_keys = sorted(parsed.keys())
    data_check_string = "\n".join(f"{key}={parsed[key][0]}" for key in sorted_keys)
 
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
 
    if computed_hash != received_hash:
        raise HTTPException(status_code=401, detail="Invalid hash")
 
    auth_date = int(parsed.get("auth_date", [0])[0])
    if int(time.time()) - auth_date > 86400:
        raise HTTPException(status_code=401, detail="Init data expired")
 
    return {key: parsed[key][0] for key in parsed}
 
 
def extract_user_info(user_data: dict) -> dict:
    """
    Telegram передаёт данные пользователя в поле 'user' как JSON-строку:
    user={"id":123,"first_name":"Ivan","username":"ivan","photo_url":"..."}
    Эта функция извлекает все нужные поля.
    """
    user_json_str = user_data.get("user")
    if user_json_str:
        try:
            user_obj = json.loads(user_json_str)
            return {
                "id":         user_obj.get("id"),
                "username":   user_obj.get("username"),
                "first_name": user_obj.get("first_name"),
                "last_name":  user_obj.get("last_name"),
                "photo_url":  user_obj.get("photo_url"),
            }
        except (json.JSONDecodeError, TypeError):
            pass
 
    # Fallback: поля могут быть напрямую в user_data (старый формат)
    return {
        "id":         user_data.get("id") or user_data.get("user_id"),
        "username":   user_data.get("username"),
        "first_name": user_data.get("first_name"),
        "last_name":  user_data.get("last_name"),
        "photo_url":  user_data.get("photo_url"),
    }
 
 
async def upsert_user(session: AsyncSession, info: dict) -> int:
    """Создаёт пользователя или обновляет его данные в БД. Возвращает telegram_id."""
    user_id = int(info["id"])
 
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()
 
    if not user:
        user = User(
            telegram_id=user_id,
            username=info.get("username"),
            first_name=info.get("first_name"),
            last_name=info.get("last_name"),
            photo_url=info.get("photo_url"),
        )
        session.add(user)
    else:
        # Обновляем данные при каждом входе
        user.username   = info.get("username")
        user.first_name = info.get("first_name")
        user.last_name  = info.get("last_name")
        user.photo_url  = info.get("photo_url")
 
    await session.commit()
    return user_id
 
 
async def get_telegram_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> int:
    # ── DEV MODE: возвращаем тестового пользователя ──────────────────
    if DEV_MODE:
        # Убеждаемся, что dev-пользователь есть в БД
        result = await session.execute(select(User).where(User.telegram_id == DEV_USER_ID))
        user = result.scalar_one_or_none()
        if not user:
            session.add(User(
                telegram_id=DEV_USER_ID,
                username="dev_user",
                first_name="Dev",
                last_name="User",
                photo_url=None,
            ))
            await session.commit()
        return DEV_USER_ID
 
    # ── PRODUCTION: полная проверка initData ─────────────────────────
    init_data: str | None = None
 
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        init_data = auth_header[len("Bearer "):]
    else:
        init_data = (
            request.headers.get("X-Telegram-Init-Data")
            or request.query_params.get("tgWebAppData")
        )
 
    if not init_data:
        raise HTTPException(status_code=401, detail="Authentication required")
 
    # Валидируем подпись
    raw_data = validate_telegram_init_data(unquote(init_data), BOT_TOKEN)
 
    # Извлекаем данные пользователя из поля "user" (JSON)
    info = extract_user_info(raw_data)
    if not info.get("id"):
        raise HTTPException(status_code=401, detail="User ID not found in initData")
 
    # Авторегистрация / обновление аватара и никнейма
    return await upsert_user(session, info)
