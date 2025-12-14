import os
import re


class Config:
    # Mandatory
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    MONGO_URI = os.getenv("MONGO_URI", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "ts_clonebot")

    # OWNER IDs – env me "1598576202 6518065496" ya "1598576202,6518065496"
    _owners_raw = os.getenv("OWNER_ID", "1598576202 6518065496")
    OWNER_IDS = [
        int(x) for x in re.split(r"[ ,]+", _owners_raw.strip()) if x.strip().isdigit()
    ]

    # Log channel & force‑sub
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003286415377"))

    _force_sub = os.getenv("FORCE_SUB", "https://t.me/serenaunzipbot")
    # URL ko username me convert
    if _force_sub.startswith("http"):
        FORCE_SUB = _force_sub.rsplit("/", 1)[-1]
    else:
        FORCE_SUB = _force_sub.lstrip("@")

    # Brand & misc
    BRAND_NAME = os.getenv("BRAND_NAME", "TECHNICAL_SERENA")
    PORT = int(os.getenv("PORT", "8080"))

    # Limits
    FREE_MAX_BATCH = int(os.getenv("FREE_MAX_BATCH", "20"))
    PREMIUM_MAX_BATCH = int(os.getenv("PREMIUM_MAX_BATCH", "200"))

    # Optional encryption key (session string ko encrypt karna ho to)
    SESSION_ENCRYPT_KEY = os.getenv("SESSION_ENCRYPT_KEY", "change-this-please")
