from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from utils.db import (
    set_premium,
    get_all_users,
    lock_channel,
    unlock_channel,
    is_channel_locked,
)


OWNER_FILTER = filters.user(Config.OWNER_IDS)


@Client.on_message(filters.command("add") & OWNER_FILTER)
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /add user_id")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user_id.")

    await set_premium(user_id, True)
    await message.reply_text(f"User `{user_id}` ko premium mein add kar diya.")


@Client.on_message(filters.command("rem") & OWNER_FILTER)
async def rem_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /rem user_id")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user_id.")

    await set_premium(user_id, False)
    await message.reply_text(f"User `{user_id}` ko premium se hata diya.")


@Client.on_message(filters.command("get") & OWNER_FILTER)
async def get_users_cmd(client: Client, message: Message):
    users = await get_all_users()
    text = "Total users: {}\n\n".format(len(users))
    text += "\n".join(str(u) for u in users[:4000])  # basic limit
    await message.reply_text(text or "No users.")


@Client.on_message(filters.command("lock") & OWNER_FILTER)
async def lock_cmd(client: Client, message: Message):
    """
    /lock         -> current chat lock
    /lock chat_id -> specific chat_id lock/unlock toggle
    """
    if len(message.command) == 1:
        chat_id = message.chat.id
    else:
        try:
            chat_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid chat_id.")

    locked = await is_channel_locked(chat_id)
    if locked:
        await unlock_channel(chat_id)
        await message.reply_text(f"Chat `{chat_id}` ko **UNLOCK** kar diya.")
    else:
        await lock_channel(chat_id)
        await message.reply_text(f"Chat `{chat_id}` ko **LOCK** kar diya.")
