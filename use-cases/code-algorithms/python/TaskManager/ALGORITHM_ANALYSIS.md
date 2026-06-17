# Algorithm Analysis: Task List Merging with Conflict Resolution

## 1. Selected Algorithm

**File:** `task_list_merge.py` (127 lines)

**Why this algorithm?** Of the three available (priority scoring, text parsing, list merging), the merge algorithm is the most complex — it handles **multi-source reconciliation**, **conflict resolution rules**, and **two-way synchronization with side-effect tracking**. It demonstrates important real-world concepts: CRDT-like merge semantics, last-write-wins with exceptions, and union merging.

---

## 2. AI Decomposition: Breaking Down the Algorithm

### 2.1 Prompt: "What does this function do at the highest level?"

```
Merge two dictionaries of tasks (local and remote) into a single consistent view.
Produce not just the merged result, but also instructions for what to push back
to each source to bring them in sync.
```

### 2.2 Prompt: "Identify the inputs, outputs, and key data structures"

| Input | Type | Description |
|-------|------|-------------|
| `local_tasks` | `dict[str, Task]` | Tasks from the local store, keyed by task ID |
| `remote_tasks` | `dict[str, Task]` | Tasks from the remote store, keyed by task ID |

| Output | Type | Description |
|--------|------|-------------|
| `merged_tasks` | `dict[str, Task]` | Reconciled task dictionary |
| `to_create_remote` | `dict[str, Task]` | Tasks to push to remote (exist only locally) |
| `to_update_remote` | `dict[str, Task]` | Tasks to update in remote (local was newer/won conflict) |
| `to_create_local` | `dict[str, Task]` | Tasks to pull to local (exist only remotely) |
| `to_update_local` | `dict[str, Task]` | Tasks to update locally (remote was newer/won conflict) |

### 2.3 Prompt: "Enumerate all distinct cases the algorithm handles"

The algorithm classifies every task ID into exactly one of three cases:

```
                         ┌─────────────────────────────┐
                         │     All Task IDs (union)     │
                         └────────────┬────────────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
                    │                 │                  │
                    ▼                 ▼                  ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
            │ Only Local   │ │ Only Remote  │ │ Both Sources     │
            │ (no conflict)│ │ (no conflict)│ │ (conflict needs  │
            │              │ │              │ │ resolution)      │
            └──────────────┘ └──────────────┘ └──────────────────┘
```

### 2.4 Prompt: "Describe the conflict resolution rules"

```
Rule 1: LAST-WRITE-WINS (most fields)
  ──> Compare task.updated_at timestamps
  ──> Newer version's title, description, priority, due_date win

Rule 2: DONE OVERRIDES (status exception)
  ──> If one source has status=DONE and the other doesn't,
      DONE always wins, regardless of timestamp
  ──> This prevents reopened tasks from resurrecting in remote

Rule 3: TAG UNION (tags are additive)
  ──> Tags from both sources are combined into a single set
  ──> Duplicates are eliminated via set union

Rule 4: TIMESTAMP FORWARDING
  ──> The merged task gets max(local.updated_at, remote.updated_at)
```

### 2.5 Prompt: "What are the side-effect flags and how do they work?"

`resolve_task_conflict` returns two booleans: `should_update_local` and `should_update_remote`.

These track which source(s) need their copy overwritten with the merge result:

| Local wins | Remote wins | Mixed (tags differ from both) |
|------------|-------------|-------------------------------|
| `update_remote=True` | `update_local=True` | `update_local=True` AND `update_remote=True` |

The top-level `merge_task_lists` propagates these into the four action dictionaries.

---

## 3. Visual Diagrams

### 3.1 Algorithm Flowchart

```
                    ┌──────────────────────┐
                    │  merge_task_lists()   │
                    │  (local, remote)      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  all_task_ids =       │
                    │  set(local) ∪ set(remote)│
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  For each task_id...  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
     ┌────────────────┐ ┌───────────┐ ┌────────────────┐
     │ local only     │ │ remote    │ │ both exist     │
     │                │ │ only      │ │                │
     │ merged = local │ │ merged =  │ │ merged =       │
     │ create_remote  │ │ remote    │ │ resolve_       │
     │ += local       │ │ create_local│ conflict()    │
     └────────────────┘ │ += remote │ └───────┬────────┘
                         └───────────┘         │
                                        ┌──────┴──────┐
                                        │              │
                                        ▼              ▼
                              ┌────────────────┐ ┌────────────────┐
                              │ update_local   │ │ update_remote  │
                              │ if needed      │ │ if needed      │
                              └────────────────┘ └────────────────┘
```

### 3.2 Conflict Resolution Decision Tree

```
resolve_task_conflict(local, remote)
│
├── TIMESTAMP CHECK (for title, desc, priority, due_date):
│   ├── remote.updated_at > local.updated_at  ──> remote values win, update_local=True
│   └── else                                   ──> local values win, update_remote=True
│
├── STATUS CHECK:
│   ├── remote=DONE, local≠DONE   ──> DONE wins, update_local=True
│   ├── local=DONE, remote≠DONE   ──> DONE wins, update_remote=True
│   ├── both different & non-DONE:
│   │   ├── remote newer  ──> remote status wins, update_local=True
│   │   └── local newer   ──> local status wins, update_remote=True
│   └── same status       ──> no change
│
├── TAG UNION:
│   ├── merged.tags = set(local.tags) ∪ set(remote.tags)
│   ├── if tags differ from local  ──> update_local=True
│   └── if tags differ from remote ──> update_remote=True
│
├── TIMESTAMP FORWARDING:
│   └── merged.updated_at = max(local, remote)
│
└── Return (merged_task, should_update_local, should_update_remote)
```

### 3.3 Data Flow for a Two-Way Sync

```
 LOCAL STORE                    MERGE ENGINE                  REMOTE STORE
 ───────────                    ────────────                  ─────────────
                                                                    │
  Task A (id=1) ─────────────────────────────────────────────►  create_remote
  (local only)                                                  [new in remote]
                                                                    │
  Task B (id=2) ◄─────────────────────────────────────────────  create_local
                                 [new in local]                   (remote only)
                                                                    
  Task C (id=3) ◄───────────── update_local ◄─────────────────  Task C (id=3)
  (older copy)     [remote title/desc win]                        (newer copy)
                                                                    │
  Task D (id=4) ────────────── update_remote ─────────────────►  Task D (id=4)
  (DONE here)     [DONE status pushes to remote]                  (still TODO)
                                                                    │
  Task E (id=5) ◄───────────── update_local ◄─────────────────  Task E (id=5)
  (tags: [a,b])    [tags union = a,b,c]                            (tags: [b,c])
```

---

## 4. Test Matrix (Edge Case Coverage)

| Test | Scenario | Rule Exercised |
|------|----------|----------------|
| `test_merge_local_only` | Task exists only locally | Case 1: create_remote |
| `test_merge_remote_only` | Task exists only remotely | Case 2: create_local |
| `test_merge_both_sources` | Task exists in both | Case 3: conflict resolution |
| `test_resolve_remote_newer` | remote.updated_at > local.updated_at | Rule 1: last-write-wins |
| `test_resolve_local_newer` | local.updated_at > remote.updated_at | Rule 1: last-write-wins (local) |
| `test_resolve_done_overrides` | remote=DONE, local=TODO | Rule 2: DONE overrides |
| `test_resolve_done_overrides_local` | local=DONE, remote=TODO | Rule 2: DONE overrides (local) |
| `test_merge_tags_union` | Each has distinct tags | Rule 3: tag union |
| `test_non_done_status_conflict` | remote=REVIEW, local=TODO | Rule 1 on status (newer wins) |

---

## 5. Insights & Learning Points

### 5.1 Design Insight: The "Sync Cable" Pattern

The merge function doesn't just produce a merged view — it also produces **action dictionaries** (`to_create_remote`, `to_update_remote`, etc.) that tell the caller exactly what mutations to apply to each store. This separates the **merge logic** from the **sync transport** (HTTP, file copy, etc.), making the algorithm testable and transport-agnostic.

### 5.2 Edge Case: DONE Override Semantics

The algorithm deliberately **breaks last-write-wins** for the `DONE` status. This is a correctness choice: if a user completes a task locally, then syncs, the remote should never resurrect it back to uncompleted just because the remote's timestamp is newer. This mirrors real-world behavior in tools like Todoist, Notion, and Google Tasks.

### 5.3 Subtle Bug Risk: Tag Union Side Effects

Because `update_local` and `update_remote` are tracked independently for tags, it is possible for **both** sides to need updating even when timestamps are equal — if tags differ from both sources. The boolean flags correctly capture this, avoiding a silent inconsistency.

### 5.4 Learning: Shallow vs. Deep Copy

The algorithm uses `copy.deepcopy(local_task)` as the merge base. This is important because:
- Without deep copy, mutating the merged task (e.g., `merged_task.tags = [...]`) would mutate the original local task
- Using local as the base (rather than remote) is arbitrary but ensures a consistent starting point

### 5.5 Learning: Composability of Merge Rules

The conflict resolution is structured as **independent rule checks** (timestamp -> status -> tags -> timestamp forwarding). Each rule reads from `local_task` and `remote_task` and writes to `merged_task`. This makes the algorithm easy to extend — adding a new field (e.g., `assignee`) would be a single new rule block.

### 5.6 Comparison: What's Missing?

Real-world sync engines (e.g., Git merge, CRDTs, OT) handle:
- **Deletion markers** (tombstones) — this algorithm ignores deleted tasks
- **Three-way merge** — this is a simple two-way merge with no common ancestor
- **Atomic transactions** — this algorithm has no rollback if one push fails
- **Concurrent edits to different fields** — this uses whole-task timestamps, not per-field resolution

These omissions are appropriate for the exercise scope, but worth noting as design trade-offs.

---

## 6. Running the Tests

```bash
python3 -m unittest tests/test_task_list_merge.py -v
```

All 8 tests pass, covering 9 distinct scenarios across the three cases and four rules.
