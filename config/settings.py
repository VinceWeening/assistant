import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
ALLOWED_TELEGRAM_USER_ID: int = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])
WEBHOOK_URL: str = os.environ.get("WEBHOOK_URL", "")
