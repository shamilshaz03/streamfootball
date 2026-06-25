"""Bot-side configuration — only the settings the bot itself needs."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")
