# Consolidated Understanding: Task Manager Application

## Architecture Overview

The application follows a strict 4-layer architecture:

```
CLI (cli.py) → Business Logic (task_manager.py) → Storage (storage.py) → Models (models.py)
```

Three algorithm utilities (`task_priority.py`, `task_parser.py`, `task_list_merge.py`) exist alongside but are **not wired into** the main application — they are only consumed by their respective test files.

**Key technologies:** Python 3 standard library only. No external dependencies. Uses `argparse` for CLI, `json` with custom encoder/decoder for persistence, `uuid` for task IDs, `unittest` for testing.

**Entry point:** `cli.py:165` — `if __name__ == "__main__": main()`

---

## Feature: Task Creation

| Layer | File:Line | Responsibility |
|-------|-----------|---------------|
| CLI | `cli.py:86-96` | Parses args (title, description, priority, due_date, tags), calls `create_task()` |
| Business Logic | `task_manager.py:12-25` | Converts int→enum for priority, parses date string, constructs `Task` |
| Storage | `storage.py:67-70` | Stores in `self.tasks` dict, calls `save()` → full JSON write |
| Model | `models.py:19-30` | Generates UUID, sets `status=TODO`, `created_at=now`, `updated_at=now` |

**Flow:** args → `TaskPriority(int)` → `datetime.strptime(due_date_str)` → `Task(...)` → `storage.add_task` → `storage.save()` → `json.dump(list(self.tasks.values()), ...)` → `tasks.json`

**Edge cases:** Invalid date format returns `None` (handled in CLI). No validation on priority value range beyond enum.

---

## Feature: Prioritization (Two Separate Systems)

### System 1: Priority Field (Integrated)

`TaskPriority` enum in `models.py:6-10` with values: `LOW=1, MEDIUM=2, HIGH=3, URGENT=4`.

Used by CLI (arg choices, display symbols), storage (serialization), and task_manager (`update_task_priority()`).

### System 2: Priority Scoring Algorithm (Standalone)

`task_priority.py` — pure functions with no side effects.

| Factor | Weight |
|--------|--------|
| Priority level | LOW=10, MEDIUM=20, HIGH=40, URGENT=60 |
| Overdue | +35 |
| Due today | +20 |
| Due in 2 days | +15 |
| Due in 7 days | +10 |
| Status = DONE | −50 |
| Status = REVIEW | −15 |
| Tags: blocker/critical/urgent | +8 |
| Updated within 1 day | +5 |

**Key discovery:** The scoring algorithm is **not imported anywhere** in the main application. `grep -rn "task_priority"` returns only the file itself and its test. The `update_task_priority()` method in `task_manager.py` only changes the enum field — it never touches the scoring algorithm.

---

## Feature: Task Completion

### Two Code Paths

| Path | Method | Fields Changed | Why separate? |
|------|--------|---------------|---------------|
| DONE | `task.mark_as_done()` | `status`, `completed_at`, `updated_at` | Completion is a rich business event — sets completion timestamp |
| Non-DONE | `storage.update_task(id, status=...)` | `status`, `updated_at` | Generic attribute change via `setattr` |

### State Changes (DONE)

```
Before:                    After:
  status: TODO               status: DONE
  completed_at: None         completed_at: 2026-06-17T14:30:00
  updated_at: earlier        updated_at: 2026-06-17T14:30:00 (= completed_at)
```

### Cascade Effects

| Feature | Effect when DONE |
|---------|-----------------|
| `is_overdue()` | Returns False (DONE tasks are never overdue) |
| `calculate_task_score()` | −50 penalty → sinks to bottom |
| `resolve_task_conflict()` | DONE overrides non-DONE regardless of timestamp |
| `get_statistics()` | Counted in `by_status["done"]` and `completed_last_week` |
| CLI display | Shows `[✓]` |

### Persistence Chain

```
mark_as_done() → storage.save() → json.dump(list(tasks), cls=TaskEncoder) → tasks.json
```

Custom `TaskEncoder` converts: enums → ints/strings, datetimes → ISO format strings. On load, `TaskDecoder.object_hook` reverses: detects Task by `id` + `title` keys, reconstructs object.

**Storage strategy:** Full-file overwrite on every change. No locking. No append log.

---

## Potential Points of Failure

1. **Stale `completed_at`** — Never cleared when moving DONE → other status. Statistics may count re-opened tasks as recently completed.
2. **Non-atomic save** — Gap between `mark_as_done()` and `save()`. Crash loses the change.
3. **Implicit `None` return** — DONE path with missing task returns `None` (falsy) instead of explicit `False`.
4. **No concurrency** — No file locking. Two simultaneous CLI invocations corrupt data.
5. **Brittle JSON encoder** — Non-serializable types on Task crash the save.

---

## Design Patterns Discovered

| Pattern | Location | Description |
|---------|----------|-------------|
| Repository | `storage.py` | Abstracts JSON behind CRUD interface |
| Adapter | `TaskEncoder`/`TaskDecoder` | Converts Python types ↔ JSON |
| Domain Event | `mark_as_done()` | Method name describes business event, not data change |
| Thin Adapter | `cli.py` | No business logic — pure arg parsing + formatting |
| DONE Override (custom pattern) | 4 locations | One business rule enforced across the stack |

---

## How Prompts Drove Understanding

| Prompt | Focus | Key Question That Changed My Understanding |
|--------|-------|------------------------------------------|
| 1: Project structure | Architecture | "Trace create → list through every layer" (became my template) |
| 2: Deepening understanding | Feature location | "Is `task_priority.py` actually called by any module?" (uncovered orphan module) |
| 3: Data flow | State changes | "What happens to `completed_at` if DONE → IN_PROGRESS?" (uncovered stale field) |

**Process that emerged:**
1. Search for keywords
2. Trace one action through all layers
3. Grep to verify assumptions about connections
4. Check test coverage for edge cases
5. Cascade — trace ripple effects across unrelated modules
