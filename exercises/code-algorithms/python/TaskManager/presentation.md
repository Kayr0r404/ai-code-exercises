# Presentation: Understanding the Task Manager Codebase

> A 3-5 minute talk about my process for understanding this codebase,
> the architecture, three key features, and what the prompts taught me.

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     CLI LAYER (cli.py)                        │
│           Entry point. Parses args, formats output.           │
│           NO business logic — just a thin adapter.            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│               BUSINESS LOGIC (task_manager.py)                │
│           Orchestrates operations, applies business rules.    │
│           Handles DONE as a special case.                     │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  STORAGE LAYER (storage.py)                   │
│       Repository pattern. In-memory dict + JSON file.        │
│       Custom encoder/decoder for datetime and enums.          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   MODEL LAYER (models.py)                     │
│     Task class, TaskPriority enum, TaskStatus enum.           │
│     Pure data + domain methods (mark_as_done, is_overdue).    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              ALGORITHM UTILITIES (standalone)                 │
│  task_priority.py  │  task_parser.py  │  task_list_merge.py   │
│  NOT wired into the main app. Only consumed by tests.         │
└──────────────────────────────────────────────────────────────┘
```

**Key point:** Strict layered architecture. Each layer talks only to the one below it. Three algorithm files are well-tested but disconnected from the running application.

---

## 2. Three Key Features

### Feature 1: Task Creation

```
User types: python cli.py create "Buy groceries" -p 3 -d "2026-06-20"

cli.py        → parses args, builds tags list
task_manager  → converts priority int→enum, parses date string
               → constructs Task object (UUID, status=TODO)
storage       → stores in dict, serializes all tasks to JSON file
```

**Surprise:** Full-file rewrite on every change, not an append log.

### Feature 2: Prioritization

Two systems share the name "priority" but are not connected:

| System | File | Integrated? |
|--------|------|-------------|
| Priority field (LOW/MED/HIGH/URGENT) | `models.py` (enum) | Yes — CLI, storage, manager |
| Priority scoring (6-factor numeric score) | `task_priority.py` | **No** — tested, never called |

The scoring considers: priority level, due date proximity, status penalties (DONE = −50, REVIEW = −15), tag boosts (+8 for blocker/critical/urgent), recency (+5 if updated within 1 day).

**Discovery:** `grep -rn "task_priority"` found only the file itself + its test. Zero imports from the app.

### Feature 3: Task Completion

Two code paths for status updates:

```
Non-DONE: storage.update_task(task_id, status=new_status)
         → only status + updated_at change

DONE:     get_task → task.mark_as_done() → save()
         → status + completed_at + updated_at change
```

**Why two paths?** Completion is a richer business event. `mark_as_done()` bundles three field changes into one atomic operation — a **Domain Event** pattern.

**Cascade effects of DONE:**
- `is_overdue()` returns False (even if completed after deadline)
- Priority score −50 (sinks to bottom)
- Merge algorithm: DONE overrides non-DONE regardless of timestamp
- Statistics: counted in "completed last week"
- CLI display: `[✓]` instead of `[ ]`

---

## 3. Interesting Design Pattern: The DONE Override Rule

**"Once a task is done, treat it as done everywhere"** — one business rule, four implementations:

| Location | What it does |
|----------|-------------|
| `mark_as_done()` | Sets `updated_at = completed_at` making completion the tiebreaker |
| `calculate_task_score()` | −50 penalty removes done tasks from priority views |
| `resolve_task_conflict()` | DONE overrides non-DONE regardless of timestamp |
| `is_overdue()` | DONE tasks are never overdue |

---

## 4. What Was Challenging & How Prompts Helped

### Hardest: The "priority" naming collision

I assumed `task_priority.py` was active because the `TaskManager` class has `update_task_priority()`. They sound connected.

**Prompt 2 fix:** "Is `task_priority.py` actually called by any other module?" → ran grep → proved it's not. Without that question, I'd still assume they're connected.

### Second hardest: Why DONE is special

I saw two code paths but didn't understand WHY.

**Prompt 3 fix:** "What happens to `completed_at` if a task goes from DONE back to IN_PROGRESS?" → traced the non-DONE path → discovered `completed_at` is never cleared → found the statistics bug → connected it to merge algorithm's DONE override. One question unlocked the whole design.

### Prompt 1's gift: The exploration exercise

"Trace `python cli.py status <task_id> done` through every layer" became the template for approaching every other feature.

---

## 5. My Process

```
For each feature:
1. SEARCH: Find all files with relevant keywords
2. TRACE: Follow one user action through every layer
3. VERIFY: Grep to confirm (or disprove) my assumptions
4. TEST: Check what tests exist and what edge cases they miss
5. CASCADE: "What else does this affect?" — trace ripple effects
```

**Biggest lesson:** Use grep to test assumptions instead of just reading code. Half the time I was wrong — those corrections were the real learning.
