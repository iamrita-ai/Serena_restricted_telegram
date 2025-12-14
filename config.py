import os


class Config:
    # Telegram API
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")

    # Bot token
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # Mongo
    MONGO_URI = os.environ.get("MONGO_URI", "")

    # Owners (default: given by you)
    OWNER_IDS = [
        int(x)
        for x in os.environ.get(
            "OWNER_IDS", "1598576202 6518065496"
        ).split()
        if x.strip()
    ]

    # Log channel (default: given by you)
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003286415377"))

    # Force Sub (username ya @username ya link ka last part)
    FORCE_SUB_CHANNEL = os.environ.get(
        "FORCE_SUB_CHANNEL",
        "serenaunzipbot"  # https://t.me/serenaunzipbot
    )

    # Brand
    BRAND_NAME = os.environ.get("BRAND_NAME", "TECHNICAL_SERENA")

    # Flask / web (for keepalive)
    PORT = int(os.environ.get("PORT", "8080"))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # Database name (optional)
    DB_NAME = os.environ.get("DB_NAME", "TECHNICAL_SERENA_DB")

    # Misc
    DEBUG = bool(int(os.environ.get("DEBUG", "0")))
