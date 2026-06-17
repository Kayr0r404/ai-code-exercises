# Journal: Mapping Data Flow — Marking a Task as Complete

## Prompt Used (Prompt 3: Mapping Data Flow and State Management)

**My filled-in prompt:**

> I'd like you to act as a senior developer who deeply understands our codebase's domain model. I'm a junior developer trying to make sense of the business logic and domain concepts in this application.
>
> Here's what I've found in the codebase:
>
> ```python
> # models.py — Task model and enums
> class TaskStatus(Enum):
>     TODO = "todo"
>     IN_PROGRESS = "in_progress"
>     REVIEW = "review"
>     DONE = "done"
>
> class Task:
>     def __init__(self, title, ...):
>         self.id = str(uuid.uuid4())
>         self.status = TaskStatus.TODO
>         self.created_at = datetime.now()
>         self.updated_at = self.created_at
>         self.completed_at = None
>
>     def mark_as_done(self):
>         self.status = TaskStatus.DONE
>         self.completed_at = datetime.now()
>         self.updated_at = self.completed_at
>
> # task_manager.py — business logic
> def update_task_status(self, task_id, new_status_value):
>     new_status = TaskStatus(new_status_value)
>     if new_status == TaskStatus.DONE:
>         task = self.storage.get_task(task_id)
>         if task:
>             task.mark_as_done()
>             self.storage.save()
>             return True
>     else:
>         return self.storage.update_task(task_id, status=new_status)
>     return False
> ```
>
> Based on this code, my current understanding is:
> - The system seems to be modeling a task tracking workflow.
> - I think Task and TaskStatus are related because every Task has a status field, and the status transitions through stages (TODO → IN_PROGRESS → REVIEW → DONE).
> - The `mark_as_done()` method appears to represent the business event of completing a task — it sets the status and also records when it was completed.
> - I'm confused about why the DONE path fetches the task and calls `mark_as_done()` directly, while non-DONE status updates go through `storage.update_task()`. Why the two different paths?
>
> Could you, as a senior developer:
> 1. Validate my current understanding, correcting any misconceptions
> 2. Help me recognize the core domain concepts represented in this code
> 3. Explain the relationships between these entities in business terms, not just technical relationships
> 4. Clarify any domain-specific terminology or patterns I might be missing
> 5. Help me connect these models to actual user-facing features or business processes
>
> Then, please ask me 3-5 questions that would test my understanding of this domain model. These should be questions that make me think about the business logic, not just the code syntax.
>
> Finally, suggest a simple diagram I could sketch to visualize these relationships that would help solidify my understanding.

---

## Senior Dev's Response

### 1. Validation of Your Understanding

You're mostly right, but let me correct one thing:

> "status transitions through stages (TODO → IN_PROGRESS → REVIEW → DONE)"

**The code does not enforce this order.** There's no validation that prevents going from TODO directly to DONE, or from REVIEW to TODO. The statuses are just string values in an enum. Any transition is allowed. The order you described is a *convention*, not a rule the code enforces. If you wanted to enforce a workflow, you'd need a state machine with allowed transitions.

Everything else you said is spot on.

### 2. Core Domain Concepts

| Concept | What it represents |
|---|---|
| **Task** | A unit of work to be tracked |
| **TaskStatus** | Where the task is in its lifecycle |
| **completed_at** | Records *when* work finished (not the same as status!) |
| **updated_at** | Tracks *any* change for merge/sync decisions |
| **mark_as_done()** | A domain event — "this task is now complete" |

The key insight: **`completed_at` is a timestamp, not a boolean.** It stores exactly when completion happened. This matters for reports ("how many tasks did we finish last week?") and for the merge algorithm (DONE overrides other statuses based on this timestamp).

### 3. Relationships in Business Terms

```
A Task moves through a lifecycle:

  Created ──→ In Progress ──→ Review ──→ Done
    │            │               │          │
    └── All tasks start here     │          │
                  └── Actively being worked  │
                                  └── Ready to verify
                                             └── Finished. completed_at set here.
```

The `Task` owns its status. No other object controls it. The status tells you:
- **What to work on next** (TODO, IN_PROGRESS)
- **What needs checking** (REVIEW)
- **What's finished** (DONE)

### 4. Why Two Different Code Paths for Status Updates?

You asked about this. Look at the two paths:

**DONE path:**
```python
task = self.storage.get_task(task_id)   # fetch full object
task.mark_as_done()                      # sets status + completed_at + updated_at
self.storage.save()                      # full file write
```

**Non-DONE path:**
```python
self.storage.update_task(task_id, status=new_status)  # generic attribute set
```

The reason: **completion is a richer business event than a status change.**

- When a task becomes DONE, three fields change: `status`, `completed_at`, `updated_at`
- When a task becomes TODO/IN_PROGRESS/REVIEW, only `status` and `updated_at` change

The generic `update_task(**kwargs)` calls `task.update(status=new_status)` which uses `setattr` — it would need three separate calls to set all three DONE fields. `mark_as_done()` bundles them into one atomic operation.

This is a **Domain Event** pattern — the method name describes what happened in business terms, not just what data changed.

### 5. Connection to User Features

| Code | User feature |
|---|---|
| `cli.py: task_manager.update_task_status(id, "done")` | User checks off a task as complete |
| `cli.py: format_task()` shows `[✓]` for DONE | Visual feedback that task is done |
| `task_manager.get_statistics()` counts completed_last_week | "What did we finish recently?" report |
| `task_list_merge.py`: DONE overrides | Preventing completed tasks from being "un-done" by sync |
| `task_priority.py`: -50 penalty for DONE | Completed tasks sink to bottom of priority list |

---

## Guided Questions & My Answers

### Q1: What happens to `completed_at` if a task goes from DONE back to IN_PROGRESS?

**What I checked:** I traced the non-DONE code path.

`task_manager.py:49-50`:
```python
return self.storage.update_task(task_id, status=new_status)
```

`storage.py:75-81`:
```python
def update_task(self, task_id, **kwargs):
    task = self.get_task(task_id)
    if task:
        task.update(**kwargs)
        ...
```

`models.py:32-36` (`update` method):
```python
def update(self, **kwargs):
    for key, value in kwargs.items():
        if hasattr(self, key):
            setattr(self, key, value)
    self.updated_at = datetime.now()
```

The call is `update_task(task_id, status=TaskStatus.IN_PROGRESS)`. This only sets `status` and `updated_at`. **`completed_at` is NOT cleared.** The task would show as IN_PROGRESS but with a `completed_at` timestamp from when it was previously done.

**Answer:** The `completed_at` field is never reset. If you move a task from DONE back to IN_PROGRESS, `completed_at` still holds the old timestamp. This could be intentional (you want to know it was *once* completed) or a bug (it should be cleared on re-open).

### Q2: If two users mark the same task as DONE at the same time, what happens?

**What I checked:** The storage layer.

`storage.py` is file-based — there's no locking:
```python
def save(self):
    with open(self.storage_path, 'w') as f:
        json.dump(..., f, cls=TaskEncoder, indent=2)
```

**Answer:** Last writer wins. If process A reads the file, process B reads the file, both modify in memory, then both write — the second write overwrites the first. There's no locking, no transaction, no conflict detection at the storage level. The merge algorithm (`task_list_merge.py`) handles this at the *sync* level, but not at the *local storage* level.

### Q3: How does the `is_overdue()` method relate to task completion?

**What I checked:**

`models.py:43-46`:
```python
def is_overdue(self):
    if not self.due_date:
        return False
    return self.due_date < datetime.now() and self.status != TaskStatus.DONE
```

**Answer:** A task is overdue if:
- It has a due date
- That due date is past
- AND the task is NOT DONE

Once a task is DONE, it can never be overdue — even if it was completed after the due date. This means "overdue" means "past deadline AND still needs work." A task that was late but is now finished is not considered overdue.

### Q4: In the `mark_as_done()` method, `updated_at` is set to `completed_at`. Why is this important?

**What I checked:**

`models.py:38-41`:
```python
def mark_as_done(self):
    self.status = TaskStatus.DONE
    self.completed_at = datetime.now()
    self.updated_at = self.completed_at  # same moment
```

**Answer:** This connects to the merge algorithm in `task_list_merge.py:98-100`:
```python
if remote_task.status == TaskStatus.DONE and local_task.status != TaskStatus.DONE:
    merged_task.status = TaskStatus.DONE
    merged_task.completed_at = remote_task.completed_at
```

The DONE override rule uses `updated_at` to decide if remote is newer. By setting `updated_at = completed_at`, the completion time becomes the "tiebreaker" timestamp. If you mark a task done at 3pm, its `updated_at` becomes 3pm. Any changes to the other copy before 3pm lose to the DONE status.

---

## Data Flow Diagram

```
User: python cli.py status <task_id> done

┌─────────────────────────────────────────────────────────────────────┐
│  CLI LAYER (cli.py)                                                 │
│                                                                     │
│  1. argparse parses: command="status", task_id="...", status="done" │
│  2. Calls: task_manager.update_task_status(task_id, "done")         │
│  3. Prints: "Updated task status to done" or error                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BUSINESS LOGIC (task_manager.py)                                   │
│                                                                     │
│  4. new_status = TaskStatus("done") → TaskStatus.DONE               │
│  5. Is it DONE? Yes → enter special path                            │
│  6. storage.get_task(task_id)                                       │
│     ─── if None → return False  (task not found)                    │
│     ─── if found → continue                                         │
│  7. task.mark_as_done()                                             │
│  8. storage.save()                                                  │
│  9. return True                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  MODEL (models.py)      │  │  STORAGE (storage.py)   │
│                         │  │                         │
│  mark_as_done():        │  │  save():                │
│  ┌─────────────────┐    │  │  ┌─────────────────┐    │
│  │ status=DONE     │    │  │ │ json.dump(      │    │
│  │ completed_at=now│    │  │ │   list(tasks),  │    │
│  │ updated_at=now  │    │  │ │   cls=Encoder   │    │
│  └─────────────────┘    │  │ │ ) → tasks.json  │    │
│                         │  │ └─────────────────┘    │
└─────────────────────────┘  └─────────────────────────┘
```

---

## State Changes During Task Completion

### Before:

```
┌────────────────────────────────────────────┐
│ Task object (in memory)                    │
│                                            │
│  id: "a1b2c3d4-..."                       │
│  title: "Fix login bug"                    │
│  status: TODO                              │  ← was TODO
│  created_at: 2026-06-16T10:00:00           │
│  updated_at: 2026-06-16T10:00:00           │
│  completed_at: None                        │  ← was None
│  due_date: 2026-06-20T00:00:00             │
└────────────────────────────────────────────┘
```

### After mark_as_done():

```
┌────────────────────────────────────────────┐
│ Task object (in memory)                    │
│                                            │
│  id: "a1b2c3d4-..."                       │
│  title: "Fix login bug"                    │
│  status: DONE                              │  ← changed!
│  created_at: 2026-06-16T10:00:00           │
│  updated_at: 2026-06-17T14:30:00           │  ← changed! (= completed_at)
│  completed_at: 2026-06-17T14:30:00         │  ← changed! (was None)
│  due_date: 2026-06-20T00:00:00             │
└────────────────────────────────────────────┘
```

### In JSON (persisted):

```json
{
  "id": "a1b2c3d4-...",
  "title": "Fix login bug",
  "status": "done",
  "updated_at": "2026-06-17T14:30:00",
  "completed_at": "2026-06-17T14:30:00",
  "due_date": "2026-06-20T00:00:00"
}
```

### Cascade effects on other features:

| Feature | Effect of DONE |
|---------|---------------|
| `is_overdue()` | Returns `False` (DONE tasks are never overdue) |
| `task_priority.calculate_task_score()` | −50 penalty → task sinks to bottom of sorted list |
| `task_list_merge.resolve_task_conflict()` | DONE overrides non-DONE regardless of timestamp |
| `get_statistics()` | Counted in `by_status["done"]` and `completed_last_week` if within 7 days |
| CLI display | Shows `[✓]` symbol instead of `[ ]` or `[>]` or `[?]` |

---

## Potential Points of Failure

### 1. No completed_at reset on un-done

If a task goes DONE → IN_PROGRESS, `completed_at` is never cleared. The statistics in `task_manager.py:105-109` would consider it "completed last week" based on `completed_at`, not current status:

```python
completed_recently = len([
    task for task in tasks
    if task.completed_at and task.completed_at >= seven_days_ago
])
```

A task that was completed a week ago but then re-opened today would still appear in this count. **Fix:** Add `and task.status == TaskStatus.DONE` to the filter.

### 2. Non-atomic save

Between `task.mark_as_done()` and `self.storage.save()`, there's a gap. If the process crashes in between, the in-memory task is marked done but the JSON file isn't updated. On next launch, `storage.load()` reads the old state from the file, and the completion is lost.

### 3. Silent failure on non-existent task ID (non-DONE path)

The non-DONE path at `task_manager.py:49-50` returns whatever `storage.update_task()` returns:

```python
return self.storage.update_task(task_id, status=new_status)
```

While `storage.py:75-81` returns `False` when the task is not found. So the caller gets `False` back. That's fine — `cli.py:108-111` handles it:
```python
if task_manager.update_task_status(args.task_id, args.status):
    print(f"Updated task status to {args.status}")
else:
    print("Failed to update task status. Task not found.")
```

But the DONE path diverges: it returns `None` implicitly if `task` is falsy but not None, or if `new_status == TaskStatus.DONE` and the task lookup fails. Actually, looking again:

```python
if new_status == TaskStatus.DONE:
    task = self.storage.get_task(task_id)
    if task:
        task.mark_as_done()
        self.storage.save()
        return True
    # falls through — no return here for not found
else:
    return self.storage.update_task(task_id, status=new_status)
```

If the task is not found in the DONE path, the method returns `None` (implicit). `cli.py` checks `if task_manager.update_task_status(...)` — `None` is falsy, so it goes to the else branch and prints "Failed to update task status. Task not found." So the behavior is the same, but it's relying on Python's truthiness of `None` rather than an explicit `return False`.

### 4. Concurrent access

As discussed in Q2, the file-based storage has no locking. Two concurrent CLI invocations can corrupt the data.

### 5. JSON encoding failures

`storage.py:7-18` — if a field contains a non-serializable type, `json.dump` raises an exception. The encoder only handles `Task`, `datetime`, and enum types. If a new field is added to `Task.__dict__` that isn't serializable (e.g., a nested object, a set, a custom class), the save will crash.

---

## How the Application Persists These Changes

### Step-by-step save chain:

```
1. task_manager: task.mark_as_done()
   │  Changes status, completed_at, updated_at in memory
   ▼
2. task_manager: self.storage.save()
   │
   ▼
3. storage.py:60  def save(self):
   │
   ▼
4. storage.py:62  open(storage_path, 'w') — opens tasks.json for writing
   │
   ▼
5. storage.py:63  json.dump(list(self.tasks.values()), f, cls=TaskEncoder, indent=2)
   │
   ├── Converts dict values to list
   ├── TaskEncoder.default() is called for each Task:
   │   ├── priority: TaskPriority.DONE → "done" (enum → string)
   │   ├── completed_at: datetime → "2026-06-17T14:30:00" (ISO format)
   │   ├── updated_at: datetime → "2026-06-17T14:30:00"
   │   └── due_date: datetime → "2026-06-20T00:00:00" (or None → null)
   ├── indent=2 makes it human-readable
   └── Output written to tasks.json
   ▼
6. File on disk (tasks.json):
   [
     {
       "id": "a1b2c3d4-...",
       "title": "Fix login bug",
       "description": "",
       "priority": 3,
       "status": "done",
       "created_at": "2026-06-16T10:00:00",
       "updated_at": "2026-06-17T14:30:00",
       "due_date": "2026-06-20T00:00:00",
       "completed_at": "2026-06-17T14:30:00",
       "tags": []
     }
   ]
```

### On next load:

```
1. storage.__init__() calls self.load()
   │
   ▼
2. storage.py:49  def load(self):
   │  if tasks.json exists:
   ▼
3. storage.py:52  json.load(f, cls=TaskDecoder)
   │
   ├── TaskDecoder.object_hook() fires for each dict:
   │   ├── Checks if dict has "id" and "title" keys (identifies a Task)
   │   ├── Creates Task object: Task(obj['title'])
   │   ├── Sets task.id = obj['id'] (restores UUID)
   │   ├── Sets task.status = TaskStatus("done") → TaskStatus.DONE
   │   ├── Sets task.completed_at = datetime.fromisoformat("2026-06-17T14:30:00")
   │   └── Sets task.updated_at = datetime.fromisoformat(...)
   ▼
4. storage.py:55-56  self.tasks[task.id] = task
   │  Task is back in memory with full state restored
```

**Key insight:** The persistence is a full-file overwrite, not an append log. Every `save()` writes the entire task list. For 10,000 tasks this would be slow, but for a CLI tool with small datasets it's fine.
