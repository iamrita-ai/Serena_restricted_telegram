import logging
import threading

from flask import Flask
from pyrogram import Client
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

log = logging.getLogger(Config.BRAND_NAME)

# Flask app (for healthcheck / keepalive)
web_app = Flask(__name__)


@web_app.route("/")
def index():
    return f"{Config.BRAND_NAME} Telegram Clone Bot is running."


def run_flask():
    web_app.run(host=Config.HOST, port=Config.PORT)


# Pyrogram Bot client (plugins root = plugins/)
bot = Client(
    name=Config.BRAND_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins={"root": "plugins"},
    workers=8,
)


if __name__ == "__main__":
    # Run Flask in separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    log.info("Starting bot...")
    bot.run()
