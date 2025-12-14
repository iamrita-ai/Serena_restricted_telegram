from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import get_user_settings, update_user_settings, reset_user_settings


SETTINGS_HELP = """
**Settings – Usage**

1️⃣ SETCHATID : Direct upload chat set karne ke liye
   `/settings SETCHATID -1001234567890`
   (ya `0` likho to wapas DM me bhejega)

2️⃣ SETRENAME : Custom rename tag / channel username
   `/settings SETRENAME [TECHNICAL_SERENA]`

3️⃣ CAPTION : Custom caption set karne ke liye
   `/settings CAPTION Ye meri custom caption hai`

4️⃣ REPLACEWORDS : Replace rules set karne ke liye
   Format: `old1:new1;old2:new2`
   Example:
   `/settings REPLACEWORDS oldchannel:newchannel;test:demo`

5️⃣ RESET : Sab settings default pe le jane ke liye
   `/settings RESET`

Note:
• Custom thumbnail / PDF watermark / video watermark yaha basic stub hain,
  tum apne hisaab se extend kar sakte ho.
"""


@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=2)

    if len(args) == 1:
        current = await get_user_settings(message.from_user.id)
        text = (
            SETTINGS_HELP
            + "\n\n**Current Settings:**\n"
            f"Upload Chat ID: `{current.get('upload_chat_id')}`\n"
            f"Rename Tag: `{current.get('rename_tag')}`\n"
            f"Caption: `{current.get('caption')}`\n"
            f"ReplaceWords: `{current.get('replace_words')}`\n"
        )
        await message.reply_text(text)
        return

    sub_cmd = args[1].upper()

    # RESET
    if sub_cmd == "RESET":
        await reset_user_settings(message.from_user.id)
        await message.reply_text("Sab settings default pe reset kar di gayi.")
        return

    if len(args) < 3:
        await message.reply_text("Invalid usage.\n\n" + SETTINGS_HELP)
        return

    value = args[2].strip()
    user_id = message.from_user.id
    current = await get_user_settings(user_id)

    if sub_cmd == "SETCHATID":
        if value in ("0", "none", "None", "dm", "DM"):
            current["upload_chat_id"] = None
        else:
            try:
                current["upload_chat_id"] = int(value)
            except ValueError:
                return await message.reply_text("chat_id galat hai. Example: `-1001234567890`")
        await update_user_settings(user_id, {"upload_chat_id": current["upload_chat_id"]})
        await message.reply_text(f"Upload chat set: `{current['upload_chat_id']}`")
        return

    if sub_cmd == "SETRENAME":
        current["rename_tag"] = value
        await update_user_settings(user_id, {"rename_tag": value})
        await message.reply_text(f"Rename tag set: `{value}`")
        return

    if sub_cmd == "CAPTION":
        current["caption"] = value
        await update_user_settings(user_id, {"caption": value})
        await message.reply_text("Custom caption set ho gayi.")
        return

    if sub_cmd == "REPLACEWORDS":
        # Format: old1:new1;old2:new2
        pairs = value.split(";")
        rw_list = []
        for p in pairs:
            if ":" in p:
                old, new = p.split(":", 1)
                rw_list.append({"old": old, "new": new})
        current["replace_words"] = rw_list
        await update_user_settings(user_id, {"replace_words": rw_list})
        await message.reply_text(f"Replace words set: `{rw_list}`")
        return

    await message.reply_text("Unknown subcommand.\n\n" + SETTINGS_HELP)
