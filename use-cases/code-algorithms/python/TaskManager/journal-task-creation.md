# Journal: Task Creation & Status Updates

## Prompt Used to Ask the AI

I filled in the template with what I knew and asked the AI to explain the feature.

**My prompt:**

> I'm a junior developer who just joined this project. I've read the README but still need help understanding the project structure and technology stack.
>
> Here's my current understanding of the project:
> - It seems to be a Task Manager application where you can create, update, list, and delete tasks.
> - It appears to use Python with no external frameworks — just standard library (argparse, json, datetime, uuid).
> - The folder structure seems to follow a simple layered architecture: CLI → Business Logic → Storage → Models.
>
> Project structure:
> ```
> TaskManager/
> ├── cli.py            # Command-line interface (user interaction)
> ├── task_manager.py   # Business logic layer
> ├── storage.py        # File-based persistence (JSON)
> ├── models.py         # Data models (Task, enums)
> ├── task_priority.py  # Priority scoring algorithm
> ├── task_parser.py    # Text parsing algorithm
> ├── task_list_merge.py# Two-way merge algorithm
> ├── tasks.json        # Data file
> └── tests/
> ```
>
> Could you:
> 1. Validate my understanding and correct any misconceptions
> 2. Identify additional key technologies, frameworks, and libraries used
> 3. Explain what each main folder likely contains and its purpose
> 4. Point out where the application entry points are located
> 5. Suggest 3-5 specific questions I should ask my team to deepen my understanding
>
> I'm particularly confused about how the `update_task_status` method in `task_manager.py` handles the DONE status differently from other statuses.
>
> After your explanation, could you suggest a small exploration exercise I could do to verify my understanding of the project structure?

---

## AI's Response

### 1. Validation

Your understanding is correct. It's a Task Manager CLI application.

| What you said | Correct? | Notes |
|---|---|---|
| Python, no external frameworks | Yes | Only standard library: `argparse`, `json`, `datetime`, `uuid`, `enum`, `os`, `re`, `copy` |
| Layered architecture | Yes | CLI → Business Logic → Storage → Models. The algorithm files (`task_priority.py`, `task_parser.py`, `task_list_merge.py`) sit alongside as utilities called by other layers. |
| Project structure | Mostly | The three algorithm files are utilities, not part of the core CRUD flow. They're used by `task_manager.py` when the user triggers priority sorting, text parsing, or merging. |

### 2. Key Technologies

- **Python 3** — no virtual environment needed, no dependencies
- **`argparse`** — CLI argument parsing
- **`json` with custom encoder/decoder** — persistence layer (not a database)
- **`uuid.uuid4()`** — generates unique task IDs
- **`unittest`** — testing framework

### 3. Folder Purpose

| File | Role |
|---|---|
| `cli.py` | Entry point. Parses user commands, calls `TaskManager` methods, formats output. |
| `task_manager.py` | Orchestrator. Contains business rules (e.g., setting `completed_at` on DONE). |
| `storage.py` | Persistence. Loads/saves `tasks.json` with custom JSON encoding for datetime/enums. |
| `models.py` | Data definitions. `Task` class, `TaskPriority` enum, `TaskStatus` enum. |
| `task_priority.py` | Algorithm: calculates importance scores, sorts tasks. |
| `task_parser.py` | Algorithm: parses free-text into structured tasks. |
| `task_list_merge.py` | Algorithm: merges two task dictionaries with conflict resolution. |
| `tests/` | Unit tests mirroring each module. |

### 4. Entry Points

There is one entry point:

- `cli.py` — run via `python cli.py <command> [options]`
- `if __name__ == "__main__": main()` at line 165

There is no `app.py` or `main.py` in the `code-algorithms` version (some other exercise variants have them).

### 5. Questions to Ask the Team

1. "Is the `tasks.json` format stable, or is it expected to change? The `TaskEncoder`/`TaskDecoder` classes would need updates if fields are added."
2. "Are there any plans to add a database backend? The current file-based approach won't handle concurrent users."
3. "The algorithm files (`task_priority.py`, `task_parser.py`, `task_list_merge.py`) are not used by the core CRUD flow in `cli.py` — are they meant to be integrated later, or are they standalone utilities?"
4. "For `update_task_status` — why does DONE use `task.mark_as_done()` while other statuses use `storage.update_task()`? Is this intentionally setting `completed_at`?"
5. "Should I write integration tests that go CLI → Manager → Storage → JSON file, or are unit tests per layer sufficient?"

### 6. Exploration Exercise

> Trace the full path of `python cli.py status <task_id> done` through every layer. Then modify `cli.py` to print "Status updated to DONE at <timestamp>" when a task is marked done, and verify it works.

---

## Main Components Involved in Task Creation/Updates

| Component | File | Responsibility |
|---|---|---|
| **CLI Layer** | `cli.py` | Parses user input, calls `TaskManager` methods, formats output. Entry point: `main()`. |
| **Business Logic Layer** | `task_manager.py` | `TaskManager` class. Contains rules: validates dates, maps enum values, handles DONE as special case. |
| **Storage Layer** | `storage.py` | `TaskStorage` class. In-memory dict + JSON serialization. CRUD operations. |
| **Model Layer** | `models.py` | `Task` class and enums (`TaskPriority`, `TaskStatus`). |

## Execution Flow: Task Creation

```
User runs: python cli.py create "Buy groceries" -p 3 -d "2026-06-20" -t "shopping,urgent"
```

```
┌─────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│ cli.py  │────▶│ task_manager │────▶│ storage   │────▶│ models   │
│ main()  │     │ .create_task │     │ .add_task │     │ Task()   │
└─────────┘     └──────────────┘     └───────────┘     └──────────┘
     │                 │                  │                 │
     │ 1. parse args   │                  │                 │
     │ 2. build tags   │                  │                 │
     │ list            │                  │                 │
     │ 3. call         │                  │                 │
     │ create_task(...)│                  │                 │
     │                 │ 4. TaskPriority  │                 │
     │                 │    (int→enum)    │                 │
     │                 │ 5. parse due     │                 │
     │                 │    date string   │                 │
     │                 │ 6. Task(title,   │                 │
     │                 │    desc, prior,  │                 │
     │                 │    due, tags)    │                 │
     │                 │                  │                 │
     │                 │ 7. add_task(task)│                 │
     │                 │                  │ 8. store in     │
     │                 │                  │    self.tasks   │
     │                 │                  │    dict         │
     │                 │                  │ 9. save() →     │
     │                 │                  │    JSON file    │
     │                 │                  │                 │
     │ 10. print       │                  │                 │
     │ task_id         │                  │                 │
```

### Steps in Detail

1. **`cli.py:86-96`** — `args.command == "create"` branch
   - Splits comma-separated tags into a list
   - Calls `task_manager.create_task(title, description, priority, due_date_str, tags)`

2. **`task_manager.py:12-25`** — `create_task()`
   - Converts `priority_value` (int) to `TaskPriority` enum
   - Parses `due_date_str` using `datetime.strptime()` if provided
   - Constructs a `Task` object (this calls `Task.__init__` which generates a UUID, sets status=TODO, timestamps)
   - Calls `self.storage.add_task(task)`

3. **`storage.py:67-70`** — `add_task()`
   - Stores task in `self.tasks` dict keyed by `task.id`
   - Calls `self.save()` which writes to `tasks.json`

4. **`storage.py:60-65`** — `save()`
   - Opens `tasks.json` for writing
   - Serializes all tasks via `TaskEncoder` (converts enums to values, datetimes to ISO strings)

## Execution Flow: Status Update (DONE)

```
User runs: python cli.py status <task_id> done
```

```
┌─────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│ cli.py  │────▶│ task_manager │────▶│ storage   │────▶│ models   │
│ main()  │     │ update_task  │     │ .save()   │     │ mark_    │
│         │     │ _status      │     │           │     │ as_done()│
└─────────┘     └──────────────┘     └───────────┘     └──────────┘
     │                 │                  │                 │
     │ 1. parse args   │                  │                 │
     │ 2. call         │                  │                 │
     │ .update_task_   │                  │                 │
     │ status(id,done) │                  │                 │
     │                 │ 3. new_status =  │                 │
     │                 │    TaskStatus(   │                 │
     │                 │    "done")       │                 │
     │                 │ 4. new_status    │                 │
     │                 │    == DONE?      │                 │
     │                 │    ↓ YES         │                 │
     │                 │ 5. get_task(id)  │                 │
     │                 │◀──── task ───────│                 │
     │                 │ 6. task.mark_    │                 │
     │                 │    as_done() ────│────────────────▶│
     │                 │                  │                 │ 7. status=DONE
     │                 │                  │                 │    completed_at=now
     │                 │                  │                 │    updated_at=now
     │                 │ 8. storage.      │                 │
     │                 │    save() ───────│                 │
     │                 │                  │ 9. JSON dump    │
     │ 10. print       │                  │                 │
     │ success msg     │                  │                 │
```

### Key Difference: DONE vs Other Statuses

In `task_manager.py:41-50`:

```python
def update_task_status(self, task_id, new_status_value):
    new_status = TaskStatus(new_status_value)
    if new_status == TaskStatus.DONE:
        task = self.storage.get_task(task_id)
        if task:
            task.mark_as_done()              # ← special path
            self.storage.save()
            return True
    else:
        return self.storage.update_task(task_id, status=new_status)  # ← generic path
```

The DONE path explicitly:
- Fetches the task object
- Calls `mark_as_done()` which sets `status=DONE`, `completed_at=now`, `updated_at=now`
- Then saves

The non-DONE path uses the generic `storage.update_task()` which calls `task.update(status=new_status)` which just sets the status and updates `updated_at` (but not `completed_at`).

## How Data Is Stored and Retrieved

### Storage Format (tasks.json)

```json
[
  {
    "id": "a1b2c3d4-...",
    "title": "Buy groceries",
    "description": "",
    "priority": 3,
    "status": "todo",
    "created_at": "2026-06-16T10:30:00",
    "updated_at": "2026-06-16T10:30:00",
    "due_date": "2026-06-20T00:00:00",
    "completed_at": null,
    "tags": ["shopping", "urgent"]
  }
]
```

### Serialization Chain

```
Task object (in memory)
    │
    ▼
TaskEncoder.default()
    ├── priority: TaskPriority.HIGH → 3 (int)
    ├── status: TaskStatus.TODO → "todo" (str)
    ├── created_at: datetime → "2026-06-16T10:30:00" (ISO string)
    └── ...same for updated_at, due_date, completed_at
    │
    ▼
json.dump() → tasks.json

--- on reload ---

tasks.json
    │
    ▼
json.load() with TaskDecoder.object_hook()
    ├── Detects Task by checking for "id" and "title" keys
    ├── Creates Task instance
    ├── priority: 3 → TaskPriority(3) → TaskPriority.HIGH
    ├── status: "todo" → TaskStatus("todo") → TaskStatus.TODO
    ├── created_at: "2026-06-16T10:30:00" → datetime.fromisoformat()
    └── ...same for other datetime fields
    │
    ▼
Task object (in memory)
```

### Retrieval Flow

```
Storage layer keeps an in-memory dict: self.tasks = {task_id: Task}
  - On init: load() reads JSON file → populates dict
  - On add/update/delete: modifies dict AND calls save()
  - get_task(task_id): dict lookup (O(1))
  - get_all_tasks(): list(dict.values())
  - get_tasks_by_status(): list comprehension filter
```

## Interesting Design Patterns Discovered

### 1. Repository Pattern

`TaskStorage` acts as a repository — it abstracts away the persistence mechanism (JSON file) behind a clean CRUD interface. The rest of the code doesn't know or care that data is stored in a file.

### 2. Custom JSON Serialization (Adapter Pattern)

`TaskEncoder` and `TaskDecoder` adapt Python objects (datetimes, enums, Task instances) to/from JSON-compatible types. This keeps the storage format human-readable while the in-memory representation uses rich types.

### 3. Special Case Pattern in update_task_status

The DONE status gets special treatment via `mark_as_done()` which sets `completed_at` in addition to changing status. Non-DONE statuses go through the generic `update()` path. This is a deliberate design choice — completing a task is semantically different from just changing its status.

### 4. Dependency Injection (Lightweight)

`TaskManager` accepts an optional `storage_path` parameter and creates its own `TaskStorage` instance. This could be refactored to accept a pre-configured storage instance for testability, but the current design still allows test isolation by pointing to a different JSON file.

### 5. CLI as a Thin Adapter

`cli.py` contains no business logic — it's a thin adapter that translates CLI arguments into method calls and formats output. This separation means the CLI could be swapped for a web API or GUI without touching the domain logic.

## Code Snippets Used for This Analysis

### Task Creation (cli.py → task_manager.py → storage.py → models.py)

**cli.py:86-96** — Create command handler:
```python
task_id = task_manager.create_task(
    args.title, args.description, args.priority, args.due, tags
)
```

**task_manager.py:12-25** — Business logic:
```python
def create_task(self, title, description="", priority_value=2,
               due_date_str=None, tags=None):
    priority = TaskPriority(priority_value)
    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    task = Task(title, description, priority, due_date, tags)
    task_id = self.storage.add_task(task)
    return task_id
```

**storage.py:67-70** — Persistence:
```python
def add_task(self, task):
    self.tasks[task.id] = task
    self.save()
    return task.id
```

**models.py:19-30** — Task initialization:
```python
def __init__(self, title, description="", priority=TaskPriority.MEDIUM,
             due_date=None, tags=None):
    self.id = str(uuid.uuid4())
    self.title = title
    self.status = TaskStatus.TODO
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.completed_at = None
```

### Status Update (cli.py → task_manager.py → models.py)

**cli.py:107-111** — Status command handler:
```python
if task_manager.update_task_status(args.task_id, args.status):
    print(f"Updated task status to {args.status}")
```

**task_manager.py:41-50** — DONE vs non-DONE branching:
```python
def update_task_status(self, task_id, new_status_value):
    new_status = TaskStatus(new_status_value)
    if new_status == TaskStatus.DONE:
        task = self.storage.get_task(task_id)
        if task:
            task.mark_as_done()
            self.storage.save()
            return True
    else:
        return self.storage.update_task(task_id, status=new_status)
```

**models.py:38-41** — mark_as_done:
```python
def mark_as_done(self):
    self.status = TaskStatus.DONE
    self.completed_at = datetime.now()
    self.updated_at = self.completed_at
```

### Storage Save/Load

**storage.py:60-65** — Save to JSON:
```python
def save(self):
    with open(self.storage_path, 'w') as f:
        json.dump(list(self.tasks.values()), f, cls=TaskEncoder, indent=2)
```

**storage.py:49-58** — Load from JSON:
```python
def load(self):
    if os.path.exists(self.storage_path):
        with open(self.storage_path, 'r') as f:
            tasks_data = json.load(f, cls=TaskDecoder)
            for task in tasks_data:
                self.tasks[task.id] = task
```
