from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import Config
from utils.db import add_user, is_premium, get_stats
from utils.text_rules import START_TEXT, HELP_TEXT, TERMS_TEXT, PLAN_TEXT, SPEEDTEST_NOT_AVAILABLE, FORCE_SUB_TEXT


async def check_force_sub(client: Client, user_id: int, message: Message = None) -> bool:
    """
    True = already subscribed
    False = not subscribed (and send join message)
    """
    if not Config.FORCE_SUB_CHANNEL:
        return True

    try:
        member = await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
        if member.status in ("kicked", "banned"):
            if message:
                await message.reply_text("Aap update channel se banned/kicked ho.")
            return False
        return True
    except Exception:
        # not a member
        if message:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Join Updates Channel",
                            url=f"https://t.me/{Config.FORCE_SUB_CHANNEL}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "✅ Joined, Refresh",
                            callback_data="refresh_fsub"
                        )
                    ],
                ]
            )
            await message.reply_text(FORCE_SUB_TEXT, reply_markup=keyboard)
        return False


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    if not await check_force_sub(client, message.from_user.id, message):
        return

    await add_user(message.from_user.id)

    try:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"#NEW_USER\nUser: {message.from_user.mention} (`{message.from_user.id}`)"
        )
    except Exception:
        pass

    text = START_TEXT.format(user_mention=message.from_user.mention)
    await message.reply_text(
        text,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^refresh_fsub$"))
async def refresh_fsub_cb(client: Client, query: CallbackQuery):
    if await check_force_sub(client, query.from_user.id, query.message):
        await query.message.edit_text("Thank you! Ab aap /start dubara bhej sakte ho.")


@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    if not await check_force_sub(client, message.from_user.id, message):
        return
    await message.reply_text(HELP_TEXT, disable_web_page_preview=True)


@Client.on_message(filters.command("terms") & filters.private)
async def terms_cmd(client: Client, message: Message):
    await message.reply_text(TERMS_TEXT, disable_web_page_preview=True)


@Client.on_message(filters.command("plan") & filters.private)
async def plan_cmd(client: Client, message: Message):
    await message.reply_text(PLAN_TEXT, disable_web_page_preview=True)


@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client: Client, message: Message):
    if message.from_user.id not in Config.OWNER_IDS:
        # Normal user ko simple stats
        s = await get_stats()
        text = (
            f"**Bot Stats**\n\n"
            f"Total Users: `{s['total_users']}`\n"
            f"Active Sessions: `{s['total_sessions']}`"
        )
        await message.reply_text(text)
        return

    # Owner ko full stats
    s = await get_stats()
    text = (
        f"**Full Bot Stats**\n\n"
        f"Total Users: `{s['total_users']}`\n"
        f"Active Sessions: `{s['total_sessions']}`\n"
        f"Locked Chats: `{s['total_locked_chats']}`"
    )
    await message.reply_text(text)


@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_cmd(client: Client, message: Message):
    premium = await is_premium(message.from_user.id)
    if premium:
        await message.reply_text("Aap **Premium User** ho ✅")
    else:
        await message.reply_text(
            "Aap **Free User** ho.\nPremium detail ke liye /plan dekho."
        )


@Client.on_message(filters.command("speedtest") & filters.private)
async def speedtest_cmd(client: Client, message: Message):
    await message.reply_text(SPEEDTEST_NOT_AVAILABLE)
