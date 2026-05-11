# Phase 6 — Self-Improvement

**Duration:** 2 weeks  
**Prerequisite:** All previous phases working  
**Goal:** The assistant demonstrably gets better over time. You can measure it.

---

## What You'll Have at the End

- `/stats` shows performance metrics: digest ratings trend, email accuracy, task completion
- Prompt versions tracked — you can see which format performed better
- Semantic memory search: "What did I decide about X?" works across months of history
- Monthly summary of what the assistant did for you
- The system automatically adjusts its behavior based on your feedback patterns

---

## Automatic Prompt Adjustment

The system reads your feedback and adjusts prompts before the next digest.

### Feedback Analysis (runs weekly, Sunday morning before digest)

```python
def analyze_feedback_and_adjust(user_id: int) -> dict:
    """
    Returns prompt adjustments based on recent feedback patterns.
    Called before generating the weekly digest.
    """
    last_4_digests = get_digests_with_feedback(user_id, limit=4)
    
    if not last_4_digests:
        return {}
    
    avg_rating = sum(d['rating'] for d in last_4_digests if d['rating']) / len(last_4_digests)
    notes = [d['rating_note'] for d in last_4_digests if d['rating_note']]
    
    # Ask Claude to extract actionable adjustments from the notes
    adjustments = claude_haiku(f"""
    The user rated the last {len(last_4_digests)} investment digests.
    Average rating: {avg_rating:.1f} (-1 to 1 scale)
    Their notes: {notes}
    
    What specific adjustments should the next digest make?
    Return JSON: {{"depth": "more|same|less", "focus_areas": [], "avoid": [], "style_note": ""}}
    """)
    
    return adjustments
```

These adjustments are injected into the digest prompt automatically.

### Prompt Version Tracking

```sql
create table prompt_versions (
  id uuid primary key default gen_random_uuid(),
  digest_type text,              -- 'investment', 'email', 'plan'
  version_tag text,              -- 'v1', 'v2', 'a/b-test-march'
  prompt_template text,
  avg_rating decimal,
  sample_size int,
  active boolean default false,
  created_at timestamptz default now()
);
```

When you change the investment prompt significantly, create a new version entry. After 4 digests, compare ratings. Keep the winner.

---

## Semantic Memory with pgvector

### Setup
```sql
-- Enable pgvector extension in Supabase
create extension if not exists vector;

alter table conversations 
  add column embedding vector(1536);  -- text-embedding-3-small dimensions

create index on conversations 
  using ivfflat (embedding vector_cosine_ops);
```

### Generating Embeddings
When storing a conversation exchange, generate an embedding:
```python
# Use OpenAI's text-embedding-3-small (cheap: $0.02/million tokens)
# Or use a free local embedding model via sentence-transformers

def store_with_embedding(user_id, role, content):
    embedding = generate_embedding(content)
    supabase.table('conversations').insert({
        'user_telegram_id': user_id,
        'role': role,
        'content': content,
        'embedding': embedding
    }).execute()
```

### Semantic Search
```python
def remember(user_id: int, query: str) -> list[dict]:
    """Find past conversations related to a query."""
    query_embedding = generate_embedding(query)
    
    result = supabase.rpc('match_conversations', {
        'query_embedding': query_embedding,
        'user_id': user_id,
        'match_count': 5,
        'similarity_threshold': 0.7
    }).execute()
    
    return result.data
```

Now when you ask "What did I decide about BESI last month?", the bot searches semantically and finds the relevant exchange even if you didn't use the exact words.

---

## `/stats` Command

```
📈 *Your assistant stats*
_Last 30 days_

**Investment digests:**
Avg rating: 0.7/1.0 ▲ (was 0.3 in month 1)
Digests sent: 4
Recommendations acted on: 2/4

**Email triage:**
Emails processed: 340
Accuracy (based on your feedback): 89%
Avg emails in digest: 4.2

**Tasks:**
Added: 23
Completed: 18 (78%)
Overdue: 3

**Goals:**
Active: 3
Avg days since last worked on: 4.2

**Usage:**
Total messages sent to you: 127
Total messages you sent: 89
Most active day: Tuesday

**API costs this month:** ~€8.40
```

---

## Monthly Summary

First day of each month, 09:00:

```
📋 *April in review*

Your assistant was active for 30 days.

**What happened:**
• Sent 4 investment digests — your ratings improved from 2/5 to 4/5
• Flagged 34 important emails, you replied to 31 of them
• Helped complete 18 tasks across 4 projects
• Sent 9 goal nudges — you responded to 7

**What got better:**
• Investment digests now focus more on EU tech (you asked for that in week 2)
• Email triage improved from 72% to 89% accuracy
• Planning nudges reduced your avg goal drift from 11 days to 4 days

**Suggestions for May:**
• Consider reviewing your BESI thesis — 3 consecutive negative weeks
• Your Wednesday calendar is consistently overloaded — want help blocking it off?
• Goal "Launch product page" is 6 weeks old — worth updating the target date?
```

---

## Self-Learning Mechanisms Summary

| Behavior | How It Learns |
|----------|--------------|
| Digest depth and style | Feedback ratings + notes → prompt adjustments |
| Email importance | Feedback on shown/hidden emails → threshold tuning |
| Planning format | Explicit feedback on weekly plan messages |
| Task natural language | Corrections when you edit parsed tasks |
| Memory recall | Semantic search grows better as database grows |
| Nudge timing | If you snooze nudges repeatedly → delay them |

---

## Definition of Done Checklist

- [ ] `/stats` command works and shows real data
- [ ] Prompt adjustment runs before each digest (verify via logs)
- [ ] pgvector extension enabled, embeddings being stored
- [ ] Semantic search works: ask about past conversation → gets relevant result
- [ ] Monthly summary fires on the 1st
- [ ] Can show, with data (avg digest rating), that quality improved from phase 4 to phase 6
- [ ] Prompt versions tracked when you make changes

---

## Where to Go After Phase 6

At this point you have a genuinely personal, learning assistant. Optional next directions:

- **Voice messages:** Send voice notes to Telegram, bot transcribes + responds
- **Outlook support:** Second email account integration  
- **Trading alerts:** Price threshold alerts for your holdings
- **Custom app:** If Telegram limitations become frustrating, build a simple web UI
- **Multi-device:** Telegram already works everywhere, but consider notifications via email for critical alerts
- **Sharing:** Multi-user support to share with a partner/family member
