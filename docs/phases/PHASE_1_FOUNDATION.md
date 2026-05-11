# Phase 1 — Foundation Bot

**Duration:** 2 weeks  
**Goal:** Working, deployed Telegram bot powered by Claude. Conversation works end-to-end.

---

## What You'll Have at the End

- A Telegram bot you can message 24/7
- It responds using Claude (Sonnet) with a system prompt that sets its personality
- Only you can use it (locked to your Telegram user ID)
- Deployed on Railway, restarts automatically if it crashes
- `/start`, `/help` commands work
- Handles errors gracefully (never crashes silently)
- Logs everything to Railway so you can debug

---

## Project Structure to Create

```
assistant/
├── main.py                    # Entry point — starts FastAPI + scheduler
├── bot/
│   ├── __init__.py
│   ├── handlers.py            # Telegram command and message handlers
│   └── middleware.py          # Security check (user ID guard)
├── ai/
│   ├── __init__.py
│   └── claude.py              # Claude API wrapper
├── config/
│   ├── __init__.py
│   └── settings.py            # Environment variable loading
├── requirements.txt
├── Procfile                   # Railway start command
├── .env.example               # Template for env vars (no real values)
└── .gitignore
```

---

## Step-by-Step Build Guide

### Step 1: Telegram Bot Setup (30 minutes)

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose a name: e.g. "My Personal Assistant"
4. Choose a username: e.g. `my_personal_ai_bot` (must end in `bot`)
5. Save the token BotFather gives you → `TELEGRAM_BOT_TOKEN`
6. Message your bot, then go to `https://api.telegram.org/bot<TOKEN>/getUpdates`
7. Find your `chat.id` in the response → `ALLOWED_TELEGRAM_USER_ID`

### Step 2: Python Project Setup (1 hour)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-telegram-bot anthropic python-dotenv httpx
pip freeze > requirements.txt
```

### Step 3: Environment Variables

Create `.env` (never commit this):
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ANTHROPIC_API_KEY=your_anthropic_key_here
ALLOWED_TELEGRAM_USER_ID=your_numeric_telegram_id
WEBHOOK_URL=https://your-railway-app.railway.app  # fill in after deploy
```

Create `.env.example` (commit this):
```env
TELEGRAM_BOT_TOKEN=
ANTHROPIC_API_KEY=
ALLOWED_TELEGRAM_USER_ID=
WEBHOOK_URL=
```

### Step 4: Settings Module

`config/settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ALLOWED_TELEGRAM_USER_ID = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
```

### Step 5: Claude Wrapper

`ai/claude.py`:
```python
import anthropic
from config.settings import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a personal AI assistant. You are smart, direct, and helpful.
You know that you will later be connected to the user's email, calendar, portfolio, and 
investment data. For now, you are a general-purpose assistant.

Be concise. Don't pad responses with unnecessary words. Use markdown formatting in your 
responses since they display in Telegram. Use bullet points for lists, **bold** for 
emphasis, and `code` for technical terms.

If asked what you can do, explain that you're being built phase by phase and currently 
handle general conversation, with email, investment, and planning features coming soon."""

def chat(messages: list[dict]) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
```

### Step 6: Telegram Handlers

`bot/handlers.py`:
```python
from telegram import Update
from telegram.ext import ContextTypes
from ai.claude import chat

# Simple in-memory conversation history (replaced by Supabase in phase 2)
conversation_history: dict[int, list[dict]] = {}

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hey {user.first_name}! I'm your personal AI assistant.\n\n"
        "I'm being built in phases — right now I can have any conversation with you. "
        "Soon I'll connect to your email, investments, and calendar.\n\n"
        "Just send me a message to get started. Use /help to see what's available."
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Available commands:*\n\n"
        "/start — Introduction\n"
        "/help — This message\n\n"
        "*Coming soon:*\n"
        "/email — Daily email triage\n"
        "/digest — Weekly investment summary\n"
        "/plan — Weekly planning\n\n"
        "Or just send me any message and I'll respond.",
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Initialize history for this user if needed
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Add user message to history
    conversation_history[user_id].append({"role": "user", "content": text})

    # Keep last 20 messages to avoid token limits
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Get Claude response
    response_text = chat(conversation_history[user_id])

    # Add assistant response to history
    conversation_history[user_id].append({"role": "assistant", "content": response_text})

    await update.message.reply_text(response_text, parse_mode="Markdown")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    import logging
    logging.error(f"Exception while handling update: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Something went wrong on my end. Try again in a moment."
        )
```

`bot/middleware.py`:
```python
from telegram import Update
from telegram.ext import BaseHandler
from config.settings import ALLOWED_TELEGRAM_USER_ID
import logging

logger = logging.getLogger(__name__)

async def user_guard(update: Update, context) -> bool:
    """Returns True if the user is allowed, False otherwise."""
    user = update.effective_user
    if user is None or user.id != ALLOWED_TELEGRAM_USER_ID:
        logger.warning(f"Blocked unauthorized user: {user.id if user else 'unknown'}")
        return False
    return True
```

### Step 7: Main Application

`main.py`:
```python
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers import start_handler, help_handler, message_handler, error_handler
from bot.middleware import user_guard
from config.settings import TELEGRAM_BOT_TOKEN, WEBHOOK_URL

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Build the Telegram application
ptb_app = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .build()
)

def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

register_handlers(ptb_app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set webhook on startup
    await ptb_app.initialize()
    if WEBHOOK_URL:
        await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info(f"Webhook set to {WEBHOOK_URL}/webhook")
    await ptb_app.start()
    yield
    # Cleanup on shutdown
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
    
    # Security guard: reject unknown users before processing
    if update.effective_user and update.effective_user.id != int(__import__('config.settings', fromlist=['ALLOWED_TELEGRAM_USER_ID']).ALLOWED_TELEGRAM_USER_ID):
        return {"ok": True}
    
    await ptb_app.process_update(update)
    return {"ok": True}
```

### Step 8: Railway Deployment Files

`Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

`.gitignore`:
```
venv/
.env
__pycache__/
*.pyc
.DS_Store
```

### Step 9: Deploy to Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app), create account
3. "New Project" → "Deploy from GitHub" → select your repo
4. Add environment variables in Railway dashboard (same as your `.env`)
5. Railway gives you a URL like `https://assistant-production.railway.app`
6. Set `WEBHOOK_URL` to this URL in Railway env vars
7. Redeploy (Railway auto-deploys on each git push after this)

### Step 10: Verify Everything Works

Test this sequence in Telegram:
- [ ] `/start` → friendly welcome message
- [ ] `/help` → command list
- [ ] "What can you do?" → intelligent response
- [ ] "What is the current EU corporate tax rate?" → factual answer
- [ ] Send 10 messages in a row → all answered correctly
- [ ] Wait 5 minutes, send another → still works
- [ ] Check Railway logs → no errors

---

## Definition of Done Checklist

- [ ] Bot responds to messages 24/7 (test at 3am by scheduling a message)
- [ ] Unauthorized Telegram users get no response (test with a second account)
- [ ] `/start` and `/help` work
- [ ] Free-form conversation works with Claude
- [ ] Typing indicator shows while Claude is thinking
- [ ] Errors are caught, user gets a friendly message
- [ ] Railway logs show clean operation
- [ ] Conversation history maintained within a session (references previous message)
- [ ] Code is pushed to GitHub, Railway deploys automatically on push

---

## Common Problems & Solutions

**Bot doesn't respond:**
- Check Railway logs for errors
- Verify webhook is set: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Make sure WEBHOOK_URL matches actual Railway URL

**Claude returns an error:**
- Check ANTHROPIC_API_KEY is correct
- Check you have API credits

**"Unauthorized" message appears:**
- Your ALLOWED_TELEGRAM_USER_ID is wrong
- Get your real ID via `@userinfobot` on Telegram

**Railway crashes on start:**
- Check all env vars are set in Railway dashboard
- Check Python version matches (use Python 3.12 in Railway settings)

---

## Next Phase Preview

Once Phase 1 is solid, Phase 2 adds:
- Supabase database for persistent conversation history
- User profile (name, timezone, preferences)
- The bot remembers everything across sessions
- Feedback buttons on responses
