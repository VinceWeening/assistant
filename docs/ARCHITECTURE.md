# System Architecture

## Overview

The assistant is a single Python service with three interaction modes:
1. **Reactive** — responds when you message it on Telegram
2. **Scheduled** — proactively sends digests at set times
3. **Triggered** — you can ask it to run something on-demand

```
┌─────────────────────────────────────────────────────┐
│                    YOU                               │
│              (Telegram app)                          │
└──────────────────┬──────────────────────────────────┘
                   │ messages
                   ▼
┌─────────────────────────────────────────────────────┐
│              Telegram Bot API                        │
│         (webhook → your server)                     │
└──────────────────┬──────────────────────────────────┘
                   │ webhook POST
                   ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Server (Railway)               │
│                                                     │
│  ┌─────────────┐   ┌──────────────┐                │
│  │  Bot Router  │   │  Scheduler   │                │
│  │  (webhooks)  │   │  (cron jobs) │                │
│  └──────┬──────┘   └──────┬───────┘                │
│         │                 │                         │
│         └────────┬────────┘                         │
│                  ▼                                  │
│         ┌────────────────┐                          │
│         │ Orchestrator   │                          │
│         │ (decides what  │                          │
│         │  to do & how)  │                          │
│         └────────┬───────┘                          │
│                  │                                  │
│        ┌─────────┼──────────┐                       │
│        ▼         ▼          ▼                       │
│  ┌──────────┐ ┌──────┐ ┌──────────┐                │
│  │  Memory  │ │  AI  │ │ Services │                │
│  │ (context)│ │Layer │ │(email,   │                │
│  └────┬─────┘ └──┬───┘ │ finance) │                │
│       │          │     └────┬─────┘                │
└───────┼──────────┼──────────┼──────────────────────┘
        │          │          │
        ▼          ▼          ▼
   Supabase    Claude API  External APIs
   (memory,    (reasoning) (Gmail, Finance,
   prefs,                   Calendar, News)
   history)
```

---

## Core Modules

### 1. Bot Router
Receives webhook events from Telegram, routes to correct handler:
- `/start` — onboarding flow
- `/digest` — trigger investment digest now
- `/email` — check emails now  
- `/plan` — weekly planning
- `/memory` — show what the bot knows about you
- Free-form text → Orchestrator

### 2. Orchestrator
The brain. Given a message or scheduled trigger:
1. Load context (memory, recent history, user profile)
2. Decide what tools/services to call (if any)
3. Call Claude with full context + tool results
4. Store the exchange in memory
5. Send response back

### 3. Memory Module
```
Conversation History
  └── last N messages per session (short-term)

User Profile
  └── name, timezone, investment style, preferences
  └── which topics matter, how detailed to go
  └── email senders who are always important

Feedback Log
  └── timestamp, digest_id, rating, note
  └── used to tune future prompts

Embeddings (Phase 2+)
  └── pgvector semantic search over past conversations
  └── "remember when I said X about Y" works
```

### 4. AI Layer
Wraps Claude API calls. Key responsibilities:
- Inject memory/context into every prompt
- Choose model (Sonnet vs Haiku) based on task complexity
- Enable prompt caching for repeated context blocks
- Structured output parsing (JSON mode for digests)

### 5. Services
Independent modules, each with a clear interface:

**EmailService**
- `get_unread_emails(since=yesterday)` → list of emails
- `score_importance(email)` → 0-1 score + reason (via Claude Haiku)
- `draft_reply(email, context)` → draft text

**InvestmentService**
- `get_portfolio()` → from Supabase (you enter positions manually)
- `get_market_data(symbols)` → via yfinance
- `get_news(topics)` → via NewsAPI
- `generate_digest(portfolio, market, news)` → via Claude Sonnet

**PlanningService**
- `get_calendar_events(week)` → via Google Calendar
- `get_tasks()` → from Supabase
- `generate_plan(events, tasks, goals)` → via Claude Sonnet

### 6. Scheduler
APScheduler jobs:
- Sunday 19:00 → investment digest
- Monday 08:00 → weekly plan
- Daily 08:00 → email triage
- (all times in your timezone, configurable)

---

## Data Flow: Weekly Investment Digest

```
Sunday 19:00 scheduler fires
    │
    ▼
InvestmentService.get_portfolio()  ←── Supabase
    │
InvestmentService.get_market_data()  ←── yfinance
    │
InvestmentService.get_news()  ←── NewsAPI
    │
Memory.get_user_profile()  ←── Supabase
Memory.get_feedback_history()  ←── Supabase (last 4 digests)
    │
    ▼
Claude Sonnet (prompt: portfolio + market + news + profile + past feedback)
    │
    ▼
Structured digest (JSON):
  - summary paragraph
  - top 3 opportunities
  - 1 risk to watch
  - recommended action
  - confidence score
    │
    ▼
Format as Telegram message (markdown)
Add inline buttons: [👍 Good] [👎 Adjust] [🔍 Tell me more]
    │
    ▼
Send to your Telegram
    │
    ▼
Store digest_id in Supabase
Wait for your button press → store feedback
```

---

## Data Flow: Conversational Message

```
You: "What do you think about buying more ASML?"
    │
    ▼
Bot Router receives message
    │
    ▼
Orchestrator:
  1. Memory.get_context() → recent chats + your profile + portfolio
  2. Detect intent: investment question
  3. InvestmentService.get_market_data(["ASML"])
  4. Claude Sonnet(message + context + market data)
  5. Memory.store_exchange(message, response)
    │
    ▼
Response sent to Telegram
```

---

## Security Architecture

- **Single-user lock**: middleware checks `update.effective_user.id == ALLOWED_USER_ID`. Any other user gets no response.
- **Secrets**: all in Railway environment variables, never in code or git
- **Google OAuth**: tokens stored in Supabase `user_tokens` table, refreshed automatically
- **Read-only external access**: no write access to any financial account ever

---

## Scalability Notes (not needed now, good to know)

This architecture is designed for one user (you). If you ever want to share it:
- Add multi-user support in Supabase (user_id on all tables)
- Move scheduler to per-user cron entries
- Add Telegram group support

For now: keep it simple, personal, fast.
