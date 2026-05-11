import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers import start_handler, help_handler, message_handler, error_handler
from bot.middleware import is_allowed
from config.settings import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, ALLOWED_TELEGRAM_USER_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ptb_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

ptb_app.add_handler(CommandHandler("start", start_handler))
ptb_app.add_handler(CommandHandler("help", help_handler))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
ptb_app.add_error_handler(error_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb_app.initialize()
    if WEBHOOK_URL:
        await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info("Webhook set to %s/webhook", WEBHOOK_URL)
    else:
        logger.warning("WEBHOOK_URL not set — webhook not registered (fine for local dev)")
    await ptb_app.start()
    yield
    await ptb_app.stop()
    await ptb_app.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)

    if not is_allowed(update):
        return {"ok": True}

    await ptb_app.process_update(update)
    return {"ok": True}
