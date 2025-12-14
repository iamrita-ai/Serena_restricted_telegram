import datetime
from typing import Optional, Dict, Any, List

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
db = mongo_client[Config.DB_NAME]

users_col = db["users"]
sessions_col = db["sessions"]
settings_col = db["settings"]
locks_col = db["locks"]


# ---------- Users / Premium ----------

async def add_user(user_id: int):
    await users_col.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "joined_at": datetime.datetime.utcnow(),
                "is_premium": False,
            }
        },
        upsert=True,
    )


async def get_all_users() -> List[int]:
    user_ids = []
    async for doc in users_col.find({}, {"_id": 1}):
        user_ids.append(doc["_id"])
    return user_ids


async def set_premium(user_id: int, value: bool = True):
    await users_col.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_premium": value,
                "premium_updated_at": datetime.datetime.utcnow(),
            }
        },
        upsert=True,
    )


async def is_premium(user_id: int) -> bool:
    doc = await users_col.find_one({"_id": user_id}, {"is_premium": 1})
    return bool(doc and doc.get("is_premium"))


# ---------- Sessions (user login) ----------

async def save_user_session(user_id: int, session_string: str):
    await sessions_col.update_one(
        {"_id": user_id},
        {
            "$set": {
                "session": session_string,
                "updated_at": datetime.datetime.utcnow(),
            }
        },
        upsert=True,
    )


async def get_user_session(user_id: int) -> Optional[str]:
    doc = await sessions_col.find_one({"_id": user_id})
    return doc.get("session") if doc else None


async def delete_user_session(user_id: int):
    await sessions_col.delete_one({"_id": user_id})


# ---------- Channel locks ----------

async def lock_channel(chat_id: int):
    await locks_col.update_one(
        {"_id": chat_id},
        {"$set": {"locked": True}},
        upsert=True,
    )


async def unlock_channel(chat_id: int):
    await locks_col.update_one(
        {"_id": chat_id},
        {"$set": {"locked": False}},
        upsert=True,
    )


async def is_channel_locked(chat_id: int) -> bool:
    doc = await locks_col.find_one({"_id": chat_id})
    return bool(doc and doc.get("locked"))


# ---------- User settings ----------

DEFAULT_SETTINGS = {
    "upload_chat_id": None,     # -100..., None = same chat with user
    "rename_tag": "",           # e.g. [TECHNICAL_SERENA]
    "caption": "",              # custom caption
    "replace_words": [],        # list of {"old": "...", "new": "..."}
    "thumbnail_id": None,       # Telegram file_id
    "pdf_watermark": "",
    "video_watermark": "",
}


async def get_user_settings(user_id: int) -> Dict[str, Any]:
    doc = await settings_col.find_one({"_id": user_id})
    if not doc:
        return DEFAULT_SETTINGS.copy()
    data = DEFAULT_SETTINGS.copy()
    data.update({k: v for k, v in doc.items() if k != "_id"})
    return data


async def update_user_settings(user_id: int, data: Dict[str, Any]):
    await settings_col.update_one(
        {"_id": user_id},
        {"$set": data},
        upsert=True,
    )


async def reset_user_settings(user_id: int):
    await settings_col.update_one(
        {"_id": user_id},
        {"$set": DEFAULT_SETTINGS},
        upsert=True,
    )


# ---------- Stats ----------

async def get_stats() -> Dict[str, Any]:
    total_users = await users_col.estimated_document_count()
    total_sessions = await sessions_col.estimated_document_count()
    total_locked_chats = await locks_col.count_documents({"locked": True})
    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "total_locked_chats": total_locked_chats,
}
