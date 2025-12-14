from config import Config

OWNER_LINK = "https://t.me/technicalserena"

START_TEXT = f"""
👋 Hi {{user_mention}},

Main **{Config.BRAND_NAME}** ka Telegram Clone/Extraction Bot hoon.

• Kisi bhi channel / group ke posts (jahan tumhara account member ho) ko
  tumhare session se fetch / forward / clone karta hoon.

• Bot ko us channel mein member hone ki zaroorat nahi hai – tumhara account
  login hoga, aur usi se saara kaam hoga.

Use at your own risk, aur hamesha Telegram / Channel rules follow karo.
"""

HELP_TEXT = f"""
**{Config.BRAND_NAME} Bot Commands:**

Admin (Owner):
• `/add user_id`  – User ko premium mein add
• `/rem user_id`  – Premium se remove
• `/get`          – Saare user IDs ki list
• `/lock`         – Current/chat_id ko lock karo (extract se rokne ke liye)

User:
• `/login`        – Tumhara account login (session generate)
• `/logout`       – Session delete + logout
• `/batch`        – Bulk extraction (chat_id, from_id, to_id)
• `/cancel`       – Ongoing batch cancel
• `/session`      – Tumhara Pyrogram v2 session string
• `/plan`         – Plans info
• `/myplan`       – Tumhara plan status
• `/settings`     – Upload chat id, caption, rename tag, etc. set karne ke liye
• `/terms`        – Terms & Conditions
• `/stats`        – Bot stats
"""

TERMS_TEXT = f"""
**Terms & Conditions – {Config.BRAND_NAME}**

1. Ye bot sirf educational aur personal backup purpose ke liye banaya gaya hai.
2. Kisi bhi type ka piracy, illegal sharing, ya channel rules ka violation
   aapki apni responsibility hai.
3. Aapka session / login info secure rakhna aapki zimmedari hai.
4. Owner (`{OWNER_LINK}`) koi bhi misuse ke liye zimmedar nahi hoga.
5. Bot kabhi bhi bina notice bandh / reset ho sakta hai.

Bot use karke aap in terms se agree kar rahe ho.
"""

PLAN_TEXT = f"""
**Premium Plans – {Config.BRAND_NAME}**

Free:
• Normal speed
• Limited batch usage

Premium:
• High speed / priority
• Zyada range batch
• Future premium features

Premium ke liye contact: {OWNER_LINK}
"""

SPEEDTEST_NOT_AVAILABLE = "Speedtest is not available in this version."

FORCE_SUB_TEXT = """
Sabse pehle hamare update channel join karo, phir /start dubara bhejo.

Without join, bot use nahi kar sakte.
"""
