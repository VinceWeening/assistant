# Personal AI Assistant — Vision

## What We're Building

A personal AI assistant that lives in your pocket, knows your life, and proactively keeps you on top of everything that matters — investments, emails, planning, and decisions. It thinks ahead, learns from you over time, and gets smarter the longer you use it.

## Core Principles

**1. One thing done perfectly before the next**
Each phase is shippable and useful on its own. We don't move to phase 2 until phase 1 feels solid. No half-built features.

**2. Proactive, not reactive**
The assistant doesn't wait for you to ask. It shows up in your inbox/app at the right moment with exactly what you need.

**3. Context-aware**
It knows your portfolio, your preferences, your goals, your communication style. Every response is personalized — not generic.

**4. Self-improving**
The system learns from your feedback (explicit thumbs up/down and implicit behavior) to get better over time without manual tuning.

**5. Private by default**
Your data lives in your own Supabase project. No third-party AI providers see your email or financial data beyond what's needed for a single API call.

---

## What It Does (Full Vision)

### Weekly Intelligence Digest
Every Sunday evening you receive:
- Market summary and what it means for YOUR portfolio specifically
- Investment opportunities worth looking at this week
- Risk signals to watch
- A recommended action (buy / hold / avoid / research more)

### Communication Triage
Every morning (or on-demand):
- Emails that need a response from you, ranked by urgency
- Draft replies for the most urgent ones
- Emails you can ignore (with reason)
- Flagged messages from important people

### Personal Planning
- Ask it to plan your week based on your calendar and goals
- It books time for deep work, reminders for deadlines
- Proactive nudges: "You haven't worked on Project X in 5 days"

### Always-On Q&A
Ask it anything — it has context about your life, your portfolio, your inbox, your goals. It's not a generic chatbot; it's YOUR assistant.

### Self-Learning Loop
- You give feedback on every digest (👍 / 👎 + optional note)
- It adjusts: which stocks to emphasize, how detailed to go, which emails matter
- Over months it becomes genuinely tuned to you

---

## Delivery Channel: Telegram

**Why Telegram over WhatsApp/SMS/custom app:**

| Option | Cost | Setup complexity | Rich UI | Proactive messages | Bot-friendly |
|--------|------|-----------------|---------|-------------------|--------------|
| Telegram | Free | Low | Yes (buttons, markdown) | Yes | Native |
| WhatsApp | Paid/API cost | High (Meta Business) | Limited | Yes (with approval) | Complex |
| SMS | Per-message cost | Medium | No | Yes | No |
| Discord | Free | Medium | Yes | Yes | Yes |
| Custom app | Dev time | Very high | Full control | Yes | Yes |

Telegram wins: free, instant setup, rich formatting, interactive buttons, proactive push messages, and excellent Python/Node.js libraries. No business account required.

---

## What Success Looks Like at Each Phase

| Phase | Done When... |
|-------|-------------|
| 1. Foundation Bot | I can talk to the bot, it responds intelligently via Claude, it's deployed |
| 2. Memory | The bot remembers conversations and knows my preferences |
| 3. Email Hub | I get a daily list of emails I actually need to act on |
| 4. Investment Intel | I get a weekly investment digest tailored to my portfolio |
| 5. Planning | I can ask the bot to plan my week and it does something useful |
| 6. Self-Improvement | The bot demonstrably adapts to my feedback over 4+ weeks |
