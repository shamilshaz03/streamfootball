import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")
ADMIN_TELEGRAM_IDS: set[int] = {
    int(x.strip()) for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip().isdigit()
}
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@12345")
BACKEND_ADMIN_USERNAME: str = os.getenv("FIRST_SUPER_ADMIN_USERNAME", "admin")
BACKEND_ADMIN_PASSWORD: str = os.getenv("FIRST_SUPER_ADMIN_PASSWORD", "Admin@12345")
