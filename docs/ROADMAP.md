# Roadmap — 12 Weeks to a Personal AI Assistant

## Philosophy

> "One thing, done perfectly, before the next."

Each phase ends with something you actually use every day. Nothing moves forward until the current phase feels right. Quality over speed.

---

## Phase Overview

| Phase | Focus | Duration | End State |
|-------|-------|----------|-----------|
| 1 | Foundation Bot | 2 weeks | Bot talks to you via Claude, deployed, always-on |
| 2 | Memory & Context | 2 weeks | Bot remembers you, learns your preferences |
| 3 | Email Intelligence | 2 weeks | Daily email triage, never miss what matters |
| 4 | Investment Digest | 2 weeks | Weekly personalized investment summary |
| 5 | Planning Assistant | 2 weeks | Bot helps plan your week, tracks goals |
| 6 | Self-Improvement | 2 weeks | Bot adapts from feedback, measurably better |

**Total: 12 weeks**

---

## Phase 1 — Foundation Bot (Weeks 1–2)

**Goal:** A working, deployed Telegram bot powered by Claude that you can have a real conversation with.

### Week 1: Core setup
- [ ] Create Telegram bot via BotFather, save token
- [ ] Set up Python project structure
- [ ] `FastAPI` + `python-telegram-bot` webhook handler
- [ ] Claude API integration (basic chat)
- [ ] Single-user security lock (your Telegram ID only)
- [ ] System prompt: who the assistant is, what it does
- [ ] `/start` command with onboarding message
- [ ] `.env` file setup, Railway account created

### Week 2: Polish & deploy
- [ ] Deploy to Railway (webhook mode, not polling)
- [ ] `/help` command listing all capabilities
- [ ] Basic conversation works end-to-end
- [ ] Handle edge cases (empty messages, errors, timeouts)
- [ ] Message rate limiting (don't spam Claude on accidental double-tap)
- [ ] Logging set up (know when things break)
- [ ] Test: 10 different conversations, all work correctly

**Definition of Done:** You can have a 10-message conversation about anything and it responds intelligently, even after a Railway restart. Bot is live 24/7.

---

## Phase 2 — Memory & Context (Weeks 3–4)

**Goal:** The bot knows who you are and remembers past conversations. Responses feel personal, not generic.

### Week 3: Database & conversation history
- [ ] Supabase project created, tables designed
- [ ] `conversations` table (message, role, timestamp, session_id)
- [ ] Store every exchange in Supabase
- [ ] Load last 20 messages as context on each request
- [ ] `/memory` command to see what bot knows about you
- [ ] Session management (new session after 1 hour gap)

### Week 4: User profile & preferences
- [ ] `user_profile` table (name, timezone, investment style, detail level preference)
- [ ] Onboarding flow: bot asks 5 questions, stores answers
- [ ] `/preferences` command to update settings
- [ ] Inject profile into every Claude prompt
- [ ] Feedback buttons (👍 / 👎) on every response
- [ ] `feedback` table — store what you liked/didn't
- [ ] Test: bot references your name and preferences naturally

**Definition of Done:** The bot greets you by name, remembers what you talked about yesterday, and adjusts detail level based on your preference. Restarting Railway doesn't lose your history.

---

## Phase 3 — Email Intelligence (Weeks 5–6)

**Goal:** Every morning you receive a Telegram message with only the emails you actually need to act on. Never miss something important again.

### Week 5: Gmail connection
- [ ] Google OAuth setup (Gmail read-only scope)
- [ ] OAuth flow via Telegram (bot sends you a link, you authenticate)
- [ ] Store Google tokens in Supabase `user_tokens` table
- [ ] Auto-refresh tokens when expired
- [ ] `EmailService.get_unread_emails()` working
- [ ] Test: bot can list your last 10 unread emails

### Week 6: Intelligence & daily digest
- [ ] Claude Haiku scores each email: importance 0-10 + category
- [ ] Categories: `needs_reply`, `fyi_only`, `marketing`, `urgent`, `ignore`
- [ ] Daily 08:00 digest: only `needs_reply` and `urgent` emails
- [ ] Format: sender, subject, one-line summary, why it matters
- [ ] Inline button: [📧 Draft Reply] — generates a draft with context
- [ ] `/email` command to trigger digest on-demand
- [ ] Important senders list (always show emails from these people)
- [ ] Tune importance scoring with your feedback over the week

**Definition of Done:** For 5 consecutive days, the morning digest correctly identifies every email you actually replied to and none of the ones you ignored.

---

## Phase 4 — Investment Intelligence (Weeks 7–8)

**Goal:** Every Sunday evening you receive a personalized investment digest: what happened, what it means for you, what to consider this week.

### Week 7: Portfolio & data feeds
- [ ] `portfolio` table in Supabase (symbol, shares, avg_buy_price, notes)
- [ ] `/portfolio` command to view and update holdings
- [ ] `yfinance` integration: prices, % change, 52-week range
- [ ] NewsAPI integration: news by stock symbol and topic
- [ ] `InvestmentService.get_market_data()` working
- [ ] Test: bot can tell you today's price for any stock you ask

### Week 8: Weekly digest
- [ ] Sunday 19:00 scheduled digest
- [ ] Claude Sonnet generates personalized analysis:
  - Portfolio performance this week
  - Key news affecting your holdings
  - Macro events to watch
  - 1-3 opportunities to research
  - Recommended action + confidence
- [ ] Digest uses your feedback from past weeks to adjust tone/depth
- [ ] Inline buttons: [👍 Useful] [👎 Adjust] [📊 More detail] [💡 Explain why]
- [ ] `/digest` command to trigger on-demand
- [ ] Feedback stored and used in next week's prompt

**Definition of Done:** After 3 weekly digests, you feel the analysis is genuinely useful and you've acted on at least one recommendation.

---

## Phase 5 — Planning Assistant (Weeks 9–10)

**Goal:** The bot helps you plan your week, tracks your goals, and nudges you proactively when you're drifting.

### Week 9: Calendar & task management
- [ ] Google Calendar integration (same OAuth as Gmail)
- [ ] `tasks` table in Supabase (title, due_date, project, status, priority)
- [ ] `goals` table (description, target_date, progress notes)
- [ ] `/task add`, `/task list`, `/task done` commands
- [ ] `/goal` commands to track long-term goals
- [ ] Monday 08:00: weekly plan message (events + tasks this week)

### Week 10: Proactive planning
- [ ] Claude generates weekly plan narrative:
  - Your calendar load this week (busy vs. light)
  - Tasks due + suggested scheduling
  - Progress on goals
  - Suggested focus for the week
- [ ] Deadline reminders (day before)
- [ ] "Haven't touched [goal] in 7 days" nudge
- [ ] `/plan` command to ask for a plan at any time
- [ ] `/plan [describe situation]` for ad-hoc planning help

**Definition of Done:** You use the weekly plan every Monday and complete more tasks than you did before having it.

---

## Phase 6 — Self-Improvement (Weeks 11–12)

**Goal:** The assistant demonstrably improves over time based on your feedback. You can measure it.

### Week 11: Feedback loops
- [ ] Feedback analytics: chart of digest ratings over time
- [ ] Automatic prompt adjustment based on feedback patterns:
  - Low ratings on investment depth → go deeper
  - Skipping email drafts → simplify email digest
  - Frequent "tell me more" → increase detail by default
- [ ] `prompt_versions` table — track which prompt performed best
- [ ] A/B test two digest formats over 2 weeks
- [ ] `/stats` command: show performance metrics

### Week 12: Advanced memory & polish
- [ ] pgvector embeddings for semantic memory search
- [ ] "What did I decide about X?" pulls relevant past conversations
- [ ] Long-term preference learning (beyond just digest rating)
- [ ] Monthly summary of what the assistant did for you
- [ ] Full system health dashboard: uptime, API costs, memory size
- [ ] Document everything for future you

**Definition of Done:** You can show, with data, that digest quality improved between week 1 and week 12. The bot correctly recalls at least 3 things you said months ago when asked.

---

## What We're NOT Building (Yet)

These are explicitly out of scope to keep quality high:

- ❌ Multi-user support — this is personal, one user only
- ❌ Web dashboard / custom app — Telegram is the UI
- ❌ Trading execution — read-only financial data only
- ❌ WhatsApp integration — Telegram is the channel
- ❌ Voice interaction — text only for now
- ❌ Complex ML training — we use Claude API, no model training

These can be phase 7+ if the core is solid.

---

## Weekly Rhythm

Each week follows the same pattern:

```
Monday:     Read the phase spec for this week
Tuesday:    Build the core feature
Wednesday:  Build the core feature
Thursday:   Integration testing
Friday:     Polish, edge cases, deploy
Weekend:    Use it. Break it. Note what feels wrong.
Next Monday: Fix what felt wrong, start next feature
```

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Gmail OAuth complexity | Medium | Allocate full week 5, have fallback (manual email forwarding) |
| Claude API costs | Low | Use Haiku for triage, Sonnet only for digests. Budget: ~$10-20/month |
| Railway downtime | Low | Set up Railway restart policy, Telegram alerts if bot goes down |
| yfinance data quality | Low | Cross-check with a secondary free source |
| Phase takes longer than 2 weeks | Medium | Don't skip — delay phase 2, not quality |
| Google token expiry | Medium | Build refresh logic in week 5, test thoroughly |
