import asyncio
from typing import Dict, Any

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PhoneNumberInvalid,
)

from config import Config
from utils.db import save_user_session, get_user_session, delete_user_session

# In‑memory login states {user_id: {...}}
LOGIN_STATE: Dict[int, Dict[str, Any]] = {}


@Client.on_message(filters.command("login") & filters.private)
async def login_cmd(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in LOGIN_STATE:
        await message.reply_text("Aap already login process mein ho. /cancel bhej ke cancel karo.")
        return

    LOGIN_STATE[user_id] = {"step": "phone"}
    await message.reply_text(
        "Apna phone number country code ke saath bhejo.\n"
        "Example: `+911234567890`",
        quote=True,
    )


@Client.on_message(filters.private & filters.text)
async def login_flow_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in LOGIN_STATE:
        return

    state = LOGIN_STATE[user_id]
    step = state.get("step")

    # Step 1: Phone number
    if step == "phone":
        phone = message.text.strip()
        state["phone"] = phone

        # Create temporary user client (no session yet)
        user_client = Client(
            name=f"user_{user_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            in_memory=True,
        )
        await user_client.connect()

        try:
            sent_code = await user_client.send_code(phone)
        except PhoneNumberInvalid:
            await message.reply_text("Invalid phone number. /login dobara bhejo.")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return

        state["step"] = "code"
        state["client"] = user_client
        state["phone_code_hash"] = sent_code.phone_code_hash

        await message.reply_text(
            "OTP aapke Telegram app ya SMS par aayega.\n"
            "Example format: `657831` (space ke bina). Ab yaha OTP bhejo.",
            quote=True,
        )
        return

    # Step 2: Code
    if step == "code":
        code = message.text.replace(" ", "").strip()
        user_client: Client = state["client"]
        phone = state["phone"]
        phone_code_hash = state["phone_code_hash"]

        try:
            await user_client.sign_in(
                phone_number=phone,
                phone_code_hash=phone_code_hash,
                phone_code=code,
            )
        except PhoneCodeInvalid:
            await message.reply_text("Galat OTP. /login se start karo.")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return
        except PhoneCodeExpired:
            await message.reply_text("OTP expire ho gaya. /login se start karo.")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return
        except SessionPasswordNeeded:
            state["step"] = "password"
            await message.reply_text(
                "Is account par 2FA password enabled hai.\n"
                "Apna Telegram password yaha bhejo.",
                quote=True,
            )
            return
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return

        # Signed in successfully (no 2FA)
        session_str = await user_client.export_session_string()
        await save_user_session(user_id, session_str)
        await user_client.disconnect()
        LOGIN_STATE.pop(user_id, None)

        await message.reply_text(
            "Login success ✅\n"
            "Ab aap /batch use karke private channels/groups se files fetch kar sakte ho "
            "(jahan aapka account member ho).",
            quote=True,
        )
        return

    # Step 3: 2FA password
    if step == "password":
        pwd = message.text
        user_client: Client = state["client"]

        try:
            await user_client.check_password(password=pwd)
        except Exception as e:
            await message.reply_text(f"Password galat hai ya error: {e}\n/login dobara try karo.")
            await user_client.disconnect()
            LOGIN_STATE.pop(user_id, None)
            return

        session_str = await user_client.export_session_string()
        await save_user_session(user_id, session_str)
        await user_client.disconnect()
        LOGIN_STATE.pop(user_id, None)

        await message.reply_text("Login success with 2FA ✅", quote=True)


@Client.on_message(filters.command("logout") & filters.private)
async def logout_cmd(bot: Client, message: Message):
    user_id = message.from_user.id
    await delete_user_session(user_id)
    LOGIN_STATE.pop(user_id, None)
    await message.reply_text("Aapka session delete ho gaya. Logout complete.")


@Client.on_message(filters.command("session") & filters.private)
async def session_cmd(bot: Client, message: Message):
    """
    Pyrogram v2 session string dikha dega
    (agar user already login hai).
    """
    user_id = message.from_user.id
    session = await get_user_session(user_id)
    if not session:
        await message.reply_text("Pehle /login karke session create karo.")
        return

    await message.reply_text(
        "Yeh aapka **Pyrogram v2 Session String** hai:\n\n"
        f"`{session}`\n\n"
        "Isko kisi ke saath share mat karo.",
        quote=True,
        disable_web_page_preview=True,
          )
