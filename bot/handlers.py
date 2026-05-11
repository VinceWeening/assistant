import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from ai.claude import chat

logger = logging.getLogger(__name__)

# In-memory conversation history keyed by user ID.
# Replaced by Supabase persistence in Phase 2.
_history: dict[int, list[dict]] = {}
_MAX_HISTORY = 20


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hey {user.first_name}! I'm your personal AI assistant.\n\n"
        "I'm being built in phases — right now I can have any conversation with you. "
        "Soon I'll connect to your email, investments, and calendar.\n\n"
        "Just send me a message to get started. Use /help to see what's available."
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_markdown(
        update,
        "*Available commands:*\n\n"
        "/start — Introduction\n"
        "/help — This message\n\n"
        "*Coming soon:*\n"
        "/email — Daily email triage\n"
        "/digest — Weekly investment summary\n"
        "/plan — Weekly planning\n\n"
        "Or just send me any message and I'll respond.",
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    history = _history.setdefault(user_id, [])
    history.append({"role": "user", "content": text})

    # Keep last N messages to stay within token limits
    if len(history) > _MAX_HISTORY:
        _history[user_id] = history[-_MAX_HISTORY:]

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    response_text = await chat(_history[user_id])
    history.append({"role": "assistant", "content": response_text})

    await _send_markdown(update, response_text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update caused error: %s", context.error, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Something went wrong on my end. Try again in a moment."
        )


async def _send_markdown(update: Update, text: str) -> None:
    """Send a message with Markdown formatting, falling back to plain text if parsing fails."""
    try:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except BadRequest:
        await update.message.reply_text(text)
