import hashlib
import hmac
import time
from urllib.parse import parse_qs, unquote
from fastapi import Request, HTTPException, status
from app.config import DEV_MODE, BOT_TOKEN

def validate_telegram_init_data(init_data: str, token: str) -> dict:
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

async def get_telegram_user(request: Request) -> int:
    if DEV_MODE:
        return 12345

    init_data = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        init_data = auth_header[len("Bearer "):]
    else:
        init_data = request.query_params.get("tgWebAppData")

    if not init_data:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_data = validate_telegram_init_data(unquote(init_data), BOT_TOKEN)
    user_id_str = user_data.get("id") or user_data.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="User ID not found in init data")
    return int(user_id_str)
