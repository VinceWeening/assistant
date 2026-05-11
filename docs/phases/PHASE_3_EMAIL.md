# Phase 3 — Email Intelligence

**Duration:** 2 weeks  
**Prerequisite:** Phase 2 complete (Supabase set up, user profile working)  
**Goal:** Daily email triage. You only see what matters. Nothing important slips through.

---

## What You'll Have at the End

- Bot checks your Gmail every morning at 08:00
- You get a clean Telegram message: only emails that need your attention
- Each email shows: sender, subject, one-line summary, why it matters
- Tap [Draft Reply] → bot writes a reply draft in your voice
- Tap [Ignore] → bot marks it as processed, won't show again
- `/email` triggers the digest on-demand anytime
- Important senders always appear, regardless of AI scoring

---

## Gmail OAuth Setup

**This is the most complex part of Phase 3. Take your time.**

### Google Cloud Console Steps
1. Go to console.cloud.google.com
2. Create a new project: "Personal Assistant"
3. Enable APIs: Gmail API, (Calendar API — you'll need it in phase 5)
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download `credentials.json`
6. Add your Gmail address as a test user (OAuth consent screen)

### Get Initial Tokens
Run this once locally to get your refresh token:
```python
# scripts/auth_google.py (run once, not part of main app)
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print("Access token:", creds.token)
print("Refresh token:", creds.refresh_token)
# Save these to your .env / Railway env vars
```

Store in Supabase `user_tokens` table (more secure than env vars for tokens):
```sql
create table user_tokens (
  user_telegram_id bigint primary key,
  google_access_token text,
  google_refresh_token text,
  google_token_expiry timestamptz,
  updated_at timestamptz default now()
);
```

---

## Email Service Architecture

```
integrations/
├── gmail.py       # Gmail API client (fetch emails, mark read)
services/
├── email_service.py    # Orchestrates: fetch → score → format → send
```

### Gmail Client (`integrations/gmail.py`)
Key functions:
```python
def get_unread_emails(since_hours: int = 24) -> list[dict]:
    """Returns list of {id, sender, subject, body_snippet, date}"""

def mark_as_processed(message_id: str):
    """Add label 'AssistantProcessed' to avoid showing twice"""
```

### Email Scoring with Claude Haiku

For each email, ask Claude Haiku (fast, cheap):
```python
def score_email(email: dict, user_profile: dict) -> dict:
    prompt = f"""Rate this email for someone named {user_profile['first_name']}.

Email:
From: {email['sender']}
Subject: {email['subject']}
Preview: {email['body_snippet']}

Important senders: {', '.join(user_profile['important_email_senders'])}

Return JSON:
{{
  "importance": 0-10,
  "category": "needs_reply|fyi_only|marketing|urgent|ignore",
  "one_line_summary": "...",
  "why_it_matters": "..." or null
}}"""
    # Use claude-haiku-4-5-20251001 for cost efficiency
```

### Daily Digest Format in Telegram

```
📧 *Your morning email digest*
_3 emails need your attention_

━━━━━━━━━━━━━━━━━━━━
🔴 *URGENT* — Jan de Vries
_Contract renewal deadline today_
"Please confirm your renewal decision by..."
[📝 Draft Reply] [✅ Handled] [🗑 Ignore]

━━━━━━━━━━━━━━━━━━━━
📬 *Reply needed* — Accountant
_Q3 invoice questions_
"I have a few questions about the Q3..."
[📝 Draft Reply] [✅ Handled] [🗑 Ignore]

━━━━━━━━━━━━━━━━━━━━
📬 *Reply needed* — Client name
_Project timeline check-in_
"Wanted to check in on the delivery date..."
[📝 Draft Reply] [✅ Handled] [🗑 Ignore]

━━━━━━━━━━━━━━━━━━━━
_34 other emails not shown (marketing, newsletters, etc.)_
[📊 See all categories]
```

### Draft Reply Flow

When you tap [Draft Reply]:
1. Bot fetches full email body from Gmail
2. Sends to Claude Sonnet with:
   - Full email content
   - Your name and writing style notes (from profile)
   - Context: "You are drafting a reply for [name]"
3. Bot sends draft as a separate message
4. Buttons: [📋 Copy to clipboard] [✏️ Adjust tone] [🔄 Regenerate]

---

## Scheduling the Daily Digest

Add to scheduler:
```python
scheduler.add_job(
    func=send_email_digest,
    trigger="cron",
    hour=8,
    minute=0,
    timezone=user_profile['timezone'],
    id="daily_email_digest"
)
```

---

## New Environment Variables

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=    # from one-time auth script
```

---

## Tuning Email Importance (End of Week 6)

After 5 days of digests, look at your feedback:
- Emails you marked "Handled" without viewing → score threshold too low, raise it
- Emails you had to find manually that weren't in digest → adjust Haiku prompt
- Add to `important_email_senders` list in your profile

---

## Definition of Done Checklist

- [ ] Gmail OAuth connected, tokens stored in Supabase
- [ ] Bot can fetch emails from last 24 hours
- [ ] Claude Haiku correctly categorizes at least 85% of emails (validate manually)
- [ ] Daily digest arrives at 08:00 in your timezone
- [ ] Digest shows only `needs_reply` and `urgent` emails
- [ ] [Draft Reply] generates a usable draft (you edit it, not rewrite it)
- [ ] [Ignore] prevents the email from appearing in future digests
- [ ] `/email` triggers digest on demand
- [ ] Important senders always appear regardless of AI score
- [ ] 5-day test: no important email missed, no junk shown

---

## Known Limitations (acceptable for now)

- Only Gmail (not Outlook/iCloud) — add others in a future phase
- Read-only — the draft is shown in Telegram, you copy-paste it to send
- No attachment reading — only text content and subject
- OAuth tokens need manual refresh if expired > 6 months (auto-refresh handles normal expiry)
