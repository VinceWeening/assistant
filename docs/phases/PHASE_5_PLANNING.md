# Phase 5 — Planning Assistant

**Duration:** 2 weeks  
**Prerequisite:** Phase 2 complete, Phase 4 recommended  
**Goal:** The bot helps you plan your week, track goals, and nudges you when you drift.

---

## What You'll Have at the End

- Monday 08:00: weekly plan in Telegram (calendar + tasks + goal progress)
- Task management via bot commands
- Goal tracking with progress notes
- Proactive nudges: deadline reminders, "you haven't worked on X in 7 days"
- `/plan` for on-demand planning help
- Ask "Plan my Thursday" and get a structured time-block suggestion

---

## Database Schema

```sql
create table tasks (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  title text not null,
  project text,                    -- optional grouping
  due_date date,
  priority int default 2,          -- 1=high, 2=medium, 3=low
  status text default 'open',      -- 'open', 'done', 'cancelled'
  notes text,
  created_at timestamptz default now(),
  completed_at timestamptz
);

create table goals (
  id uuid primary key default gen_random_uuid(),
  user_telegram_id bigint not null,
  title text not null,
  description text,
  target_date date,
  status text default 'active',    -- 'active', 'completed', 'paused'
  progress_notes text[],           -- append-only log of progress notes
  last_worked_on timestamptz,
  created_at timestamptz default now()
);
```

---

## Google Calendar Integration

Uses the same OAuth credentials as Gmail (phase 3).  
Add `https://www.googleapis.com/auth/calendar.readonly` to your scopes.

```python
# integrations/calendar.py
def get_week_events(start_date, end_date) -> list[dict]:
    """Returns list of {title, start, end, location, is_all_day}"""
```

---

## Weekly Plan Format

Monday 08:00 Telegram message:

```
📅 *Your week — May 12–18*

**Calendar:**
Mon: 10:00 Team standup (30m), 14:00 Client call (1h)
Tue: Free
Wed: 09:00 Dentist (1h), 15:00 Investor meeting (2h)
Thu: Free
Fri: 10:00 1:1 with accountant (1h)

**Tasks due this week:**
🔴 Submit Q2 tax documents — due Wednesday
🟡 Review contractor invoices — due Friday  
🟢 Update portfolio spreadsheet — no deadline

**Goal progress:**
🎯 Launch new product page — Last worked on: 5 days ago
🎯 Read 2 books this month — 1/2 done ✅

---
**Suggested focus:**
Given your Wednesday meetings, block Tuesday for deep work on the tax documents. 
Thursday is your best day for the product page — no meetings, good energy.

Keep Friday light — end-of-week admin only.
```

---

## Bot Commands

**Tasks:**
- `/task add Review Q2 invoices by Friday` — adds task (Claude parses natural language)
- `/task list` — shows open tasks grouped by priority/project
- `/task done [id or title]` — marks complete
- `/tasks today` — just today's tasks

**Goals:**
- `/goal add Launch new website by July 1` — creates goal
- `/goal list` — shows active goals with last-worked date
- `/goal update Product page — finished the hero section` — appends progress note

**Planning:**
- `/plan` — generates weekly plan now
- `/plan Thursday` — time-block suggestions for one day
- `/plan I have 2 hours free this afternoon, what should I do?` — ad-hoc planning

---

## Proactive Nudges

**Deadline reminders** — day before due date, 09:00:
```
⏰ Reminder: "Submit Q2 tax documents" is due tomorrow.
[✅ Mark done] [📅 Snooze 1 day] [🗑 Remove]
```

**Goal drift nudge** — if last_worked_on > 7 days, 10:00 any day:
```
💡 You haven't worked on "Launch new product page" in 9 days.
Want to schedule some time for it this week?
[📅 Add to this week] [⏸ Pause goal] [I'm on it]
```

**Weekly review prompt** — Friday 17:00:
```
🔄 End of week check-in. How did it go?
Tasks completed: 3/5
Goals touched: 1/2

What should carry over to next week? [Reply or /plan to start fresh]
```

---

## Natural Language Task Parsing

When you say `/task add Review Q2 invoices before Friday urgent`:

Send to Claude Haiku:
```
Extract task details from: "Review Q2 invoices before Friday urgent"
Return JSON: {"title": "...", "due_date": "YYYY-MM-DD", "priority": 1|2|3, "project": null|"..."}
Today is {date}. Assume "Friday" means this Friday.
```

---

## Definition of Done Checklist

- [ ] Tasks: add, list, done all work
- [ ] Goals: add, list, update all work
- [ ] Google Calendar fetches this week's events
- [ ] Monday 08:00 weekly plan fires with calendar + tasks + goals
- [ ] Plan narrative is actually useful (test for 2 weeks)
- [ ] Deadline reminders fire day before
- [ ] Goal drift nudge fires after 7 days
- [ ] `/plan` on-demand works
- [ ] Natural language task parsing works (try 10 different phrasings)
- [ ] Friday review prompt fires at 17:00

---

## What Good Looks Like (After 2 Weeks)

You start your Monday by reading the plan and it actually reflects your week accurately. You complete more tasks than before because the bot reminds you. You don't drift on goals for more than a week without a nudge.
