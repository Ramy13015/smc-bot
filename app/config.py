import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL = os.getenv("CHANNEL", "telegram")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
