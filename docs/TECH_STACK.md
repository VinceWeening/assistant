# Tech Stack

Every choice here is made with "less moving parts, more working software" in mind.

---

## Delivery Layer

**Telegram Bot**
- Library: `python-telegram-bot` (async, well-maintained, full API coverage)
- Why: Free, instant, supports buttons/markdown/files/voice, proactive push, works everywhere

---

## Backend

**Language: Python 3.12**
- Why: Best ecosystem for AI/data/API integrations
- Simpler than TypeScript for background jobs and data processing
- All the financial/AI libraries we need exist and are mature

**Framework: FastAPI**
- Handles Telegram webhooks
- Serves any internal API endpoints
- Async-native, fast, minimal boilerplate

**Scheduler: APScheduler**
- Runs weekly investment digests, daily email checks
- Runs inside the same Python process — no separate queue system needed yet

---

## AI Layer

**Claude API (Anthropic)**
- Model: `claude-sonnet-4-6` for main reasoning tasks
- Model: `claude-haiku-4-5-20251001` for quick classification/triage (cheaper, faster)
- Prompt caching: enabled for all long context (memory, portfolio data)
- Why Claude: Best reasoning quality, tool use, long context, and we have SDK access

---

## Database & Memory

**Supabase (PostgreSQL)**
- Conversation history
- User profile and preferences
- Portfolio positions
- Email/message metadata
- Feedback logs (what the user liked/disliked)
- `pgvector` extension for semantic memory search (phase 2+)

**Why Supabase:**
- Managed PostgreSQL — no server to maintain
- pgvector built in for embeddings
- REST API auto-generated
- Already have MCP tooling set up

---

## Integrations (by phase)

| Integration | API/Method | Phase |
|-------------|-----------|-------|
| Telegram | Bot API | 1 |
| Claude | Anthropic Python SDK | 1 |
| Supabase | supabase-py | 2 |
| Gmail | Google OAuth + Gmail API | 3 |
| Yahoo Finance | `yfinance` (free, no key) | 4 |
| News | NewsAPI.org (free tier) or RSS | 4 |
| Google Calendar | Google OAuth + Calendar API | 5 |

---

## Hosting

**Railway**
- Why not Vercel: Vercel is serverless — bad for long-running bots, background schedulers, and persistent connections
- Railway: runs a standard Python process, supports cron, cheap (~$5/month), simple deploys from GitHub
- Alternative: Render (free tier, but cold starts), Fly.io (good performance)

**Deployment flow:**
```
Push to GitHub → Railway auto-deploys → Bot restarts → All good
```

---

## Development Environment

```
assistant/
├── bot/                    # Telegram bot handlers
├── services/               # Business logic (email, investments, planning)
├── memory/                 # Supabase interactions, context building
├── scheduler/              # APScheduler jobs
├── ai/                     # Claude API wrappers, prompt templates
├── integrations/           # Gmail, Calendar, Finance API clients
├── config/                 # Settings, environment variables
├── docs/                   # All planning documents (this folder)
└── tests/                  # Tests per phase
```

---

## Environment Variables (will grow per phase)

```env
# Phase 1
TELEGRAM_BOT_TOKEN=
ANTHROPIC_API_KEY=
ALLOWED_TELEGRAM_USER_ID=   # Your personal Telegram ID — blocks everyone else

# Phase 2
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# Phase 3
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=

# Phase 4
NEWS_API_KEY=               # newsapi.org free tier

# Phase 5
# Uses same Google OAuth from phase 3 (Calendar + Gmail same credentials)
```

---

## Security Notes

- Bot is locked to your personal Telegram user ID from day 1
- All secrets in environment variables, never in code
- Google OAuth tokens stored in Supabase (encrypted at rest)
- No financial account write access — read-only data feeds only
