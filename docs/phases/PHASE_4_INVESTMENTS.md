# Phase 4 — Investment Intelligence

**Duration:** 2 weeks  
**Prerequisite:** Phase 2 complete (memory/profile working)  
**Goal:** Every Sunday evening, a personalized investment digest that's actually useful.

---

## What You'll Have at the End

- Your portfolio stored in Supabase (you input your positions)
- `/portfolio` to view and update holdings
- Sunday 19:00: weekly investment digest in Telegram
- Digest: portfolio performance, relevant news, opportunities, one recommended action
- Digest adapts to your feedback week by week
- `/digest` triggers the digest on-demand
- Ask questions like "What do you think about ASML?" and get real data + analysis

---

## Portfolio Storage

```sql
create table portfolio (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  symbol text not null,           -- 'ASML', 'AAPL', 'BTC-USD'
  shares decimal not null,
  avg_buy_price decimal,          -- in EUR or USD (note the currency)
  currency text default 'EUR',
  asset_type text default 'stock', -- 'stock', 'etf', 'crypto', 'bond'
  notes text,                     -- why you own it, your thesis
  added_at timestamptz default now(),
  unique (user_telegram_id, symbol)
);

create table investment_digests (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  generated_at timestamptz default now(),
  content jsonb,                  -- full structured digest
  telegram_message_id text,
  rating int,                     -- -1, 0, 1
  rating_note text
);
```

---

## Data Sources (All Free)

### yfinance (Yahoo Finance)
```python
import yfinance as yf

def get_stock_data(symbols: list[str]) -> dict:
    data = {}
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1wk")
        data[symbol] = {
            "price": info.get("currentPrice"),
            "week_change_pct": calculate_week_change(hist),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "pe_ratio": info.get("trailingPE"),
            "analyst_target": info.get("targetMeanPrice"),
        }
    return data
```

### NewsAPI (free tier: 100 requests/day)
```python
# newsapi.org — free account
def get_news_for_portfolio(symbols: list[str], company_names: list[str]) -> list[dict]:
    # Search for each company name + "stock" or "earnings"
    # Return top 3 articles per holding
    # Deduplicate macro news (market-wide events)
```

### Macro Context (no API needed)
Use Claude's knowledge for macro context:
- "What were the major market events this week relevant to [sectors]?"
- Claude's knowledge + news articles = good enough macro summary

---

## Weekly Digest Generation

### Prompt Structure for Claude Sonnet
```
You are a personal investment analyst for {name}.

## Their Portfolio
{formatted portfolio with current prices and week performance}

## Relevant News This Week
{top news articles for their holdings}

## Their Profile
Investment style: {style}
Risk tolerance: {level}
Goals: {goals}

## Past Digest Feedback
Last week rating: {rating}
Note: {note}
{if low rating: "They found the last digest too generic — be more specific to their holdings"}

## Task
Generate a weekly investment digest. Be specific to THEIR portfolio, not generic advice.

Return JSON:
{
  "headline": "one sentence summary of the week",
  "portfolio_summary": "paragraph on their portfolio's week",
  "top_news_impact": [{"holding": "ASML", "news": "...", "impact": "positive/neutral/negative", "action": "..."}],
  "macro_context": "paragraph on broader market",
  "opportunities": ["specific opportunity 1", "specific opportunity 2"],
  "risk_to_watch": "one specific risk for their portfolio",
  "recommended_action": "specific action with reasoning",
  "confidence": "high/medium/low"
}
```

### Digest Telegram Format
```
📊 *Weekly Investment Digest*
_Week of May 11–17, 2026_

**This week:** Tech outperformed as rate cut expectations rose. Your portfolio +2.3%.

---
**Your holdings:**
✅ ASML +4.1% — Earnings beat, orders strong. Hold thesis intact.
➡️ MSFT +1.2% — Neutral week, Azure growth on track.
⚠️ BESI -2.8% — Semiconductor equipment demand softer than expected.

---
**Key news:**
• ASML Q1 results exceeded expectations — order backlog at record high
• ECB signals potential rate cut in June — positive for growth stocks

---
**Macro context:**
[paragraph]

---
**This week's recommendation:**
Consider trimming BESI position — 3 consecutive weeks of order weakness. See if Q2 guidance reverses trend before adding.

*Confidence: Medium*

---
[👍 Useful] [👎 Needs adjustment] [📊 More detail] [💡 Explain BESI]
```

---

## Bot Commands

**`/portfolio`**
```
Your portfolio:
• ASML: 15 shares @ €680 avg — Current: €712 (+4.7%)
• MSFT: 20 shares @ $380 avg — Current: $415 (+9.2%)  
• BESI: 50 shares @ €92 avg — Current: €87 (-5.4%)

Total value: €28,450
Week change: +€640 (+2.3%)

[➕ Add holding] [✏️ Edit] [🗑 Remove]
```

**`/digest`** — triggers full digest immediately

**`/ask ASML`** — deep dive on a specific holding

---

## Feedback Loop (Critical)

When you rate a digest:
- 👍 → note what worked, store with digest
- 👎 → ask a follow-up: "What was missing or wrong?" → store note

The next week's prompt includes the last 4 ratings and notes. Claude adjusts automatically.

After 4 weeks, you should notice the digests becoming noticeably more relevant.

---

## Definition of Done Checklist

- [ ] Portfolio stored and viewable via `/portfolio`
- [ ] `/portfolio` add/edit/remove commands work
- [ ] yfinance returns correct prices for all your holdings
- [ ] NewsAPI returns relevant articles for your holdings
- [ ] Sunday 19:00 digest fires and arrives in Telegram
- [ ] Digest references your actual holdings with correct numbers
- [ ] Feedback buttons work and store rating in Supabase
- [ ] `/digest` on-demand trigger works
- [ ] After 2 digests, the third one references past feedback
- [ ] Ask "What do you think about ASML?" → bot fetches live data and responds

---

## Cost Estimate

- yfinance: free
- NewsAPI: free (100 req/day, we use ~10)
- Claude Sonnet for weekly digest: ~$0.05/week
- Claude Haiku for email triage (phase 3): ~$0.10/day
- **Total monthly estimate: ~$5–10 in Claude API costs**
