import threading
from flask import Flask
from config import Config
from pyrogram import Client

# Pyrogram Bot Client (plugins root = plugins/)
bot = Client(
    "TECHNICAL_SERENA_BOT",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# Simple Flask app for keep-alive / healthcheck
flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return f"{Config.BRAND_NAME} Clone Bot is running.", 200


def run_flask():
    flask_app.run(host="0.0.0.0", port=Config.PORT)


def run_bot():
    bot.run()


if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t2 = threading.Thread(target=run_flask)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
