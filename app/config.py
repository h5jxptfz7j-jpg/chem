import os
from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "True").lower() in ("true", "1", "yes")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_telegram_bot_token")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./telegram_mini_app.db")