# Phase 2 — Memory & Context

**Duration:** 2 weeks  
**Prerequisite:** Phase 1 complete and stable  
**Goal:** The bot knows who you are, remembers everything, and responds like someone who knows you.

---

## What You'll Have at the End

- Every conversation stored in Supabase — survives restarts
- Bot greets you by name, references past conversations naturally
- You've done a one-time onboarding (5 questions the bot asks)
- Your preferences (detail level, timezone, interests) stored and used
- Feedback buttons on every response (👍/👎)
- `/memory` shows what the bot knows about you
- `/preferences` lets you update your profile

---

## Database Schema

Run these in the Supabase SQL editor:

```sql
-- Conversation history
create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  session_id text not null,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

create index on conversations (user_telegram_id, created_at desc);

-- User profile
create table user_profile (
  user_telegram_id bigint primary key,
  first_name text,
  timezone text default 'Europe/Amsterdam',
  investment_style text, -- 'conservative', 'moderate', 'aggressive'
  preferred_detail_level text default 'medium', -- 'brief', 'medium', 'detailed'
  important_email_senders text[], -- array of email addresses
  goals_summary text, -- free text, updated over time
  onboarding_complete boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Feedback on assistant responses
create table feedback (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  message_id text, -- Telegram message ID
  context_type text, -- 'conversation', 'email_digest', 'investment_digest'
  rating int check (rating in (-1, 1)), -- -1 = thumbs down, 1 = thumbs up
  note text, -- optional free-text note
  created_at timestamptz default now()
);
```

---

## New Project Structure

```
assistant/
├── memory/
│   ├── __init__.py
│   ├── db.py              # Supabase client
│   ├── conversations.py   # Store/retrieve conversation history
│   └── profile.py         # User profile CRUD
├── bot/
│   ├── handlers.py        # Updated with onboarding, memory commands
│   └── onboarding.py      # 5-question onboarding flow
... (rest same as phase 1)
```

---

## Key Implementation Notes

### Supabase Client (`memory/db.py`)
```python
from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
```

### Session Management
A "session" is a continuous conversation. New session = 60+ minute gap between messages.
```python
import hashlib
from datetime import datetime, timedelta

def get_session_id(user_id: int, last_message_time: datetime | None) -> str:
    now = datetime.utcnow()
    if last_message_time is None or (now - last_message_time) > timedelta(hours=1):
        # New session
        return hashlib.md5(f"{user_id}-{now.date()}-{now.hour}".encode()).hexdigest()[:12]
    return None  # caller should reuse existing session_id
```

### Context Building (injected into every Claude call)
```python
def build_context(user_id: int) -> str:
    profile = get_user_profile(user_id)
    recent = get_recent_messages(user_id, limit=20)
    
    context = f"""## About the user
Name: {profile['first_name']}
Timezone: {profile['timezone']}
Investment style: {profile['investment_style']}
Prefers: {profile['preferred_detail_level']} level of detail
Goals: {profile['goals_summary']}

## Recent conversation history
{format_messages(recent)}"""
    return context
```

### Onboarding Flow
The bot asks 5 questions on first `/start`:
1. "What's your name?" (stores `first_name`)
2. "What timezone are you in? (e.g. Europe/Amsterdam)" (stores `timezone`)
3. "How would you describe your investment style? [Conservative / Moderate / Aggressive]" (inline buttons)
4. "How much detail do you want in my responses? [Brief / Medium / Detailed]" (inline buttons)
5. "What are you currently working on or focused on?" (stores `goals_summary`)

After completing: "Perfect! I've saved your profile. I'll remember this going forward."

### Feedback Buttons
After every assistant message, add inline keyboard:
```
[👍] [👎]
```
When pressed → store in feedback table → edit the buttons to show "Thanks for the feedback!"

---

## Updated Claude Call with Context

```python
def chat_with_context(user_id: int, new_message: str) -> str:
    context = build_context(user_id)
    
    # Retrieve recent conversation for Claude's messages list
    recent_messages = get_recent_messages_as_claude_format(user_id, limit=20)
    recent_messages.append({"role": "user", "content": new_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT + f"\n\n{context}",
        messages=recent_messages,
    )
    return response.content[0].text
```

---

## Definition of Done Checklist

- [ ] All conversations stored in Supabase (verify by querying directly)
- [ ] Bot survives a Railway restart without losing history
- [ ] Onboarding runs automatically for new users
- [ ] `/memory` shows your stored profile and recent topics
- [ ] `/preferences` lets you change timezone, detail level
- [ ] Bot references your name and past context naturally in responses
- [ ] Feedback buttons appear after every message
- [ ] Feedback stored correctly in Supabase
- [ ] Session breaks correctly after 1 hour gap

---

## Common Problems

**Supabase connection fails:**
- Check SUPABASE_URL format: `https://xxxx.supabase.co`
- Use service key (not anon key) for server-side operations

**History too long, Claude errors:**
- Limit to last 20 messages, trim to 15 if approaching token limit
- Summarize old history in one message if needed (future optimization)

**Onboarding gets stuck:**
- Store onboarding step in user_profile.onboarding_step (int)
- Each answer advances the step; check step on every message
