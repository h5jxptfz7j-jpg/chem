from fastapi import APIRouter, Depends, Request
from urllib.parse import unquote
import json

@router.get("/debug-init")
async def debug_init(request: Request):
    auth = request.headers.get("Authorization", "")
    init_data = auth[len("Bearer "):] if auth.startswith("Bearer ") else ""
    
    # Показываем сырые данные
    raw = unquote(init_data)[:500]
    
    # Пробуем распарсить user поле
    user_obj = None
    try:
        from urllib.parse import parse_qs
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
