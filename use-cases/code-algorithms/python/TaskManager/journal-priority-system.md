# Journal: Task Prioritization System

## Prompt Used (Prompt 2: Deepen Understanding)

**My filled-in prompt:**

> I need to work on the **task prioritization feature** in this codebase, but I'm not sure where the code for this feature lives.
>
> My approach so far:
> - I've searched for keywords like `priority`, `task_priority`, `sort_tasks`
> - I looked in the root directory `task_priority.py` and `models.py` (where TaskPriority enum lives) which seemed relevant
> - I think the feature might relate to `task_manager.py` since it has an `update_task_priority` method, and possibly `cli.py` where priorities are displayed
>
> Project structure:
> ```
> TaskManager/
> ├── cli.py
> ├── task_manager.py
> ├── storage.py
> ├── models.py
> ├── task_priority.py
> ├── tasks.json
> └── tests/
>     ├── test_task_priority.py
>     └── test_task_manager.py
> ```
>
> Based on my search, these files might be relevant, but I'm not sure:
> - `task_priority.py` — seems to be the core algorithm
> - `models.py` — contains `TaskPriority` enum (LOW, MEDIUM, HIGH, URGENT)
> - `task_manager.py` — has `update_task_priority()` method
> - `cli.py` — has `priority` command and displays priority symbols
>
> Can you help me:
> 1. Evaluate my search approach and suggest improvements
> 2. Identify which files and directories most likely contain the implementation for this feature
> 3. Suggest specific search terms or patterns that would be more effective
> 4. Explain what parts of the feature might be located in different areas of the codebase
> 5. Recommend a step-by-step investigation process to understand the complete feature flow
>
> Also, what questions could I ask myself as I'm exploring the code to ensure I'm on the right track? What specific patterns should I look for to confirm I've found all the relevant parts?
>
> After your guidance, could you give me a small challenge to test my understanding of how to navigate this feature's code?

---

## AI's Guided Questions & My Answers

The AI responded with these guided questions. I explored the code to answer each one.

### Q1: Is `task_priority.py` actually called by any other module, or is it standalone?

**What I checked:** I searched for imports of `task_priority` across the entire codebase.

```bash
grep -rn "task_priority" . --include="*.py"
```

**What I found:**

| File | Matches |
|------|---------|
| `tests/test_task_priority.py` | `from task_priority import calculate_task_score, sort_tasks_by_importance, get_top_priority_tasks` |
| `task_priority.py` | (self-references in its own file) |

**That's it.** No import in `task_manager.py`. No import in `cli.py`. No import in `storage.py`.

**Answer:** The priority scoring engine is **completely standalone**. It is not wired into the main application flow at all. The only consumer is its own test file.

**Misconception clarified:** I assumed `task_priority.py` was part of the active feature set. It's actually a module that exists alongside the app but is never called by it. The priority system has two separate concerns:

1. **Priority as a task field** (LOW/MEDIUM/HIGH/URGENT enum) — fully integrated into CRUD
2. **Priority scoring algorithm** (numeric score calculation) — a standalone utility not connected to the UI

---

### Q2: What does `update_task_priority` in `task_manager.py` actually do — and does it touch `task_priority.py`?

**What I checked:** I read the full method in `task_manager.py:52-54`:

```python
def update_task_priority(self, task_id, new_priority_value):
    new_priority = TaskPriority(new_priority_value)
    return self.storage.update_task(task_id, priority=new_priority)
```

**What I traced:**

```
cli.py:114       → task_manager.update_task_priority(task_id, 3)
task_manager:52  → TaskPriority(3)           # int → enum conversion
task_manager:53  → storage.update_task(...)   # delegates to storage
storage.py:75    → task.update(priority=...)  # calls Task.update()
storage.py:78    → task.update() sets attr + bumps updated_at
storage.py:79    → self.save()               # writes JSON
```

**Answer:** This is just changing a task's priority **level** (e.g., from MEDIUM to HIGH). It has nothing to do with the scoring algorithm in `task_priority.py`. The naming collision is unfortunate — "priority" means two different things here.

---

### Q3: Where is the `TaskPriority` enum used across the whole codebase?

**What I checked:** I searched for `TaskPriority` usage.

**What I found:**

| Location | Usage |
|----------|-------|
| `models.py:6-10` | Enum definition: `LOW=1, MEDIUM=2, HIGH=3, URGENT=4` |
| `models.py:19-20` | Task constructor: default `priority=TaskPriority.MEDIUM` |
| `storage.py:11` | Encoder: `obj.priority.value` (serialize to int) |
| `storage.py:28` | Decoder: `TaskPriority(obj['priority'])` (deserialize from int) |
| `task_manager.py:14` | `TaskPriority(priority_value)` in `create_task()` |
| `task_manager.py:36` | `TaskPriority(priority_filter)` in `list_tasks()` |
| `task_manager.py:53` | `TaskPriority(new_priority_value)` in `update_task_priority()` |
| `cli.py:18-22` | Priority symbols: `LOW="!", MEDIUM="!!", ...` |
| `cli.py:42` | CLI arg choices: `[1, 2, 3, 4]` |
| `cli.py:59` | CLI arg choices for update command |
| `task_priority.py:8-13` | Score weights: `LOW:1, MEDIUM:2, HIGH:4, URGENT:6` |
| `tests/test_task_priority.py` | Extensively used in test fixtures |
| `tests/test_task_manager.py` | Used in priority update tests |

**Answer:** The enum is the bridge between the two priority systems. The CLI, storage, and task_manager all use it for the priority **field**. The scoring algorithm also reads it to compute weights.

---

### Q4: What factors does the scoring algorithm actually consider? Are there any that surprised you?

**What I checked:** I read `calculate_task_score()` in `task_priority.py:5-45` and broke down every factor:

| Factor | Weight | Why it matters | Did I expect it? |
|--------|--------|----------------|------------------|
| Priority level | `LOW:10, MED:20, HIGH:40, URGENT:60` | Base importance | Yes |
| Overdue | `+35` | Past deadline, urgent to complete | Yes |
| Due today | `+20` | Same-day deadline | Yes |
| Due in 2 days | `+15` | Approaching deadline | Yes |
| Due in 7 days | `+10` | Moderate urgency | Yes |
| Status = DONE | `−50` | Should not appear high in priority list | Yes |
| Status = REVIEW | `−15` | Nearly done, lower priority | No, this surprised me |
| Tags: blocker/critical/urgent | `+8` | Manually flagged as important | No, didn't expect tag-based boosting |
| Updated within 1 day | `+5` | Recently worked on, might need attention | No, recency boost was unexpected |

**Surprises:**
- The REVIEW status penalty (−15) — I wouldn't have thought REVIEW tasks should be deprioritized
- Tag-based boosting for `blocker`/`critical`/`urgent` — I assumed tags were just for organization
- Recency boost — a task updated recently gets +5 even if nothing else changed about it

---

### Q5: Can `get_top_priority_tasks` crash? What happens with empty input, negative limits, or zero tasks?

**What I checked:** I read the function and the test cases.

```python
def get_top_priority_tasks(tasks, limit=5):
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

And `sort_tasks_by_importance`:

```python
def sort_tasks_by_importance(tasks):
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks
```

**Test coverage:**

| Scenario | Test | Result |
|----------|------|--------|
| Empty list | `get_top_priority_tasks([], limit=3)` | Returns `[]` |✅|
| Default limit | `get_top_priority_tasks(tasks)` | Returns top 5 |✅|
| limit=3 with 7 tasks | `get_top_priority_tasks(tasks, limit=3)` | Returns 3 |✅|
| Negative limit | Not tested | Python returns `[]` (slicing handles it) |⚠️ untested |
| limit=0 | Not tested | Returns `[]` |⚠️ untested |
| None as tasks | Not tested | Would crash with TypeError |⚠️ untested |

**Answer:** Basic cases work. Edge cases around the `limit` parameter and `None` input are not tested.

---

### Q6: Are there integration tests that test the priority scoring through the CLI or the TaskManager layer?

**What I checked:** I searched for tests that call priority scoring through `task_manager.py` or `cli.py`.

```bash
grep -n "calculate_task_score\|sort_tasks_by_importance\|get_top_priority" tests/test_task_manager.py
```

**Result:** No matches. The test_manager tests only test `update_task_priority` (the field change), not the scoring algorithm.

**Answer:** The scoring algorithm has **zero integration tests**. It's only tested in isolation via `tests/test_task_priority.py`. The application never calls it at all.

---

## Initial Understanding vs. What I Discovered

| What I thought | What I discovered |
|---|---|
| `task_priority.py` is part of the active feature flow | It's **completely disconnected** from the app — no module imports it |
| `update_task_priority()` uses the scoring algorithm | It just changes the priority **field** (enum value), no scoring involved |
| Priority is just the LOW/MEDIUM/HIGH/URGENT level | There are **two priority systems**: the enum field and the numeric scoring algorithm |
| The scoring algorithm only considers priority level and due date | It also considers: status penalties, tag boosts, and recency boosts |
| All features are wired together in the CLI | The scoring/sorting feature has no CLI command — it exists but is inaccessible to users |

## Key Insights the Guided Questions Uncovered

1. **Naming collision hazard:** "Priority" means two different things in this codebase — a static field (enum value on a Task) and a dynamic score (computed by `calculate_task_score`). A junior could easily confuse them.

2. **Orphan module:** The scoring algorithm is well-tested in isolation but completely unused by the application. It's either a work-in-progress, a library for future use, or leftover from a different exercise variant.

3. **Scoring weights are arbitrary:** The weights (×10 for priority, +35 for overdue, −50 for done, +8 for tags) have no justification in comments or docs. There's no explanation for why REVIEW is −15 vs. DONE being −50, or why the recency boost is +5.

4. **`task_priority.py` is testable by design:** It uses pure functions with no side effects — no storage, no I/O, no global state. The tests mock `datetime.now()` to control time. This is good design even if the module isn't wired in yet.

## My Challenge Response

**The AI's challenge:** "Trace what happens end-to-end when a user creates a task with `--priority 4`, then runs the `list` command. Now trace what would need to change to make `list` display tasks sorted by the scoring algorithm instead of insertion order."

### Trace 1: Create → List (current flow)

```
User: python cli.py create "Fix login bug" --priority 4

cli.py:87-96     create task with priority=4
task_manager:12  TaskPriority(4) → URGENT
task_manager:23  Task(title="Fix login bug", priority=URGENT)
models.py:19     Task.__init__: self.priority = URGENT
storage.py:67    add_task(task): stores in dict, saves to JSON

User: python cli.py list

cli.py:99        task_manager.list_tasks()
task_manager:39  return self.storage.get_all_tasks()
storage.py:90    return list(self.tasks.values())
cli.py:101-102   iterates in dict insertion order, prints each
```

Tasks are displayed in **dict insertion order**, not by priority score.

### Trace 2: What would need to change for score-based sorting

```
Changes needed:

1. task_manager.py — list_tasks():
   - Add a param like sort_by_score=False
   - When True, import task_priority and call
     sort_tasks_by_importance() before returning

2. cli.py — list command:
   - Add --sort-by-score flag to argparse
   - Pass it through to task_manager.list_tasks()

3. (Optional) Make it the default:
   - Change list_tasks() to always sort by score
   - This changes existing behavior, so check with the team first
```

No changes to `models.py`, `storage.py`, or `task_priority.py` itself.

---

## Summary

The prioritization system has two separate parts that share a name but are not connected:

```
PRIORITY FIELD (integrated)          PRIORITY SCORING (standalone)
┌─────────────────────────┐          ┌─────────────────────────┐
│ models.py: TaskPriority │          │ task_priority.py        │
│   enum (LOW/MED/...)    │          │   calculate_task_score  │
│                         │          │   sort_by_importance    │
│ task_manager.py         │          │   get_top_priority      │
│   update_task_priority  │          │                         │
│   create_task(priority) │          │ TESTS ONLY              │
│                         │          │   test_task_priority.py │
│ cli.py                  │          │                         │
│   --priority flag       │          │ NOT CALLED BY APP       │
│   priority symbols      │          └─────────────────────────┘
│   in format_task()      │
└─────────────────────────┘
```

The scoring algorithm is well-designed (pure functions, tested, mock-friendly) but is not wired into the application. Connecting it would be straightforward — add a `--sort-by-score` flag to the CLI's `list` command and call `sort_tasks_by_importance()` in the `list_tasks()` method.
