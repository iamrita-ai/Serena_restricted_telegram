import os
import time
from typing import Dict

from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from utils.db import get_user_session, is_channel_locked, get_user_settings
from utils.progress import progress_for_pyrogram

# user_id -> cancel flag
BATCH_CANCEL: Dict[int, bool] = {}


async def get_user_client(user_id: int, session: str) -> Client:
    user_client = Client(
        name=f"user_{user_id}",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=session,
        in_memory=True,
    )
    await user_client.connect()
    return user_client


@Client.on_message(filters.command("batch") & filters.private)
async def batch_cmd(bot: Client, message: Message):
    """
    Usage:
      /batch chat_id from_id to_id

    Example:
      /batch -1001234567890 1 100
    """
    user_id = message.from_user.id
    session = await get_user_session(user_id)
    if not session:
        await message.reply_text("Pehle /login karke apna session set karo.")
        return

    if len(message.command) != 4:
        return await message.reply_text(
            "Usage:\n`/batch chat_id from_id to_id`\n\n"
            "Example:\n`/batch -1001234567890 1 100`",
            quote=True,
        )

    try:
        chat_id = int(message.command[1])
        start_id = int(message.command[2])
        end_id = int(message.command[3])
    except ValueError:
        return await message.reply_text("chat_id, from_id, to_id numbers hone chahiye.")

    if await is_channel_locked(chat_id):
        return await message.reply_text(
            "Yeh channel owner ne lock kar diya hai. Extraction allowed nahi hai."
        )

    if start_id > end_id:
        start_id, end_id = end_id, start_id

    user_settings = await get_user_settings(user_id)
    upload_chat_id = user_settings.get("upload_chat_id") or message.chat.id
    rename_tag = user_settings.get("rename_tag", "")
    custom_caption = user_settings.get("caption", "")
    replace_words = user_settings.get("replace_words", [])

    status = await message.reply_text(
        f"Batch started...\nChat: `{chat_id}`\nRange: `{start_id}` to `{end_id}`",
        quote=True,
    )

    BATCH_CANCEL[user_id] = False

    user_client = await get_user_client(user_id, session)

    base_download_dir = os.path.join("downloads", str(user_id))
    os.makedirs(base_download_dir, exist_ok=True)

    sent_count = 0
    failed_count = 0

    try:
        for msg_id in range(start_id, end_id + 1):
            if BATCH_CANCEL.get(user_id):
                break

            try:
                orig = await user_client.get_messages(chat_id, msg_id)
            except Exception:
                failed_count += 1
                continue

            if not orig or not orig.media:
                continue

            # Download
            try:
                start_time = time.time()
                file_path = await user_client.download_media(
                    orig,
                    file_name=base_download_dir,
                )
            except Exception:
                failed_count += 1
                continue

            # Prepare caption
            caption = custom_caption or (orig.caption or "")
            if rename_tag:
                caption = f"{caption}\n\n{rename_tag}".strip()

            # Replace words if configured
            for rw in replace_words:
                old = rw.get("old")
                new = rw.get("new", "")
                if old:
                    caption = caption.replace(old, new)

            # Send
            try:
                if orig.document:
                    msg = await bot.send_document(
                        chat_id=upload_chat_id,
                        document=file_path,
                        caption=caption or None,
                        progress=progress_for_pyrogram,
                        progress_args=(status, start_time, "Uploading Document"),
                    )
                elif orig.video:
                    msg = await bot.send_video(
                        chat_id=upload_chat_id,
                        video=file_path,
                        caption=caption or None,
                        progress=progress_for_pyrogram,
                        progress_args=(status, start_time, "Uploading Video"),
                    )
                elif orig.audio:
                    msg = await bot.send_audio(
                        chat_id=upload_chat_id,
                        audio=file_path,
                        caption=caption or None,
                        progress=progress_for_pyrogram,
                        progress_args=(status, start_time, "Uploading Audio"),
                    )
                elif orig.photo:
                    msg = await bot.send_photo(
                        chat_id=upload_chat_id,
                        photo=file_path,
                        caption=caption or None,
                        progress=progress_for_pyrogram,
                        progress_args=(status, start_time, "Uploading Photo"),
                    )
                else:
                    # For any other media
                    msg = await bot.send_document(
                        chat_id=upload_chat_id,
                        document=file_path,
                        caption=caption or None,
                        progress=progress_for_pyrogram,
                        progress_args=(status, start_time, "Uploading File"),
                    )

                sent_count += 1
            except Exception:
                failed_count += 1
            finally:
                # Server se file hamesha ke liye delete
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                except Exception:
                    pass

        await status.edit_text(
            f"Batch finished.\n\n"
            f"Sent: `{sent_count}`\n"
            f"Failed: `{failed_count}`\n"
            f"Cancelled: `{BATCH_CANCEL.get(user_id)}`"
        )
    finally:
        await user_client.disconnect()
        BATCH_CANCEL.pop(user_id, None)


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(bot: Client, message: Message):
    user_id = message.from_user.id
    BATCH_CANCEL[user_id] = True
    await message.reply_text("Ongoing batch cancel request set. Thodi der mein ruk jayega.")
