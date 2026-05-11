import logging
from telegram import Update
from config.settings import ALLOWED_TELEGRAM_USER_ID

logger = logging.getLogger(__name__)


def is_allowed(update: Update) -> bool:
    user = update.effective_user
    if user is None or user.id != ALLOWED_TELEGRAM_USER_ID:
        logger.warning("Blocked unauthorized user: %s", user.id if user else "unknown")
        return False
    return True
