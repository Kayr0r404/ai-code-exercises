# Test Plan — Task Priority System

## Part 1: Behavior Analysis — calculateTaskScore

### Edge Cases Identified

| # | Test Case | Input | Expected Behavior | Reason |
|---|-----------|-------|-------------------|--------|
| 1 | No due date, no tags, default priority | Task with title only, priority=MEDIUM | Score = 20 (2 × 10, no modifiers) | Baseline — verifies no bonuses/penalties applied incorrectly |
| 2 | Overdue task | Priority=MEDIUM, dueDate=yesterday | Score = 50 (20 + 30 overdue) | Overdue bonus is the largest due-date boost |
| 3 | Due today task | Priority=MEDIUM, dueDate=today | Score = 40 (20 + 20 today) | Today bonus is distinct from overdue |
| 4 | Due in 3-7 days | Priority=MEDIUM, dueDate=+5 days | Score = 30 (20 + 10 week-range) | Boundary: 7-day bracket |
| 5 | Completed task | Priority=MEDIUM, status=DONE, no dueDate | Score = -30 (20 - 50) | Completed penalty reduces below zero |
| 6 | Review status task | Priority=MEDIUM, status=REVIEW, no dueDate | Score = 5 (20 - 15) | Review penalty is smaller than DONE |
| 7 | Critical tag boost | Priority=MEDIUM, tags=['critical'], no dueDate | Score = 28 (20 + 8) | Tags bonus applied |
| 8 | Urgent tag boost | Priority=MEDIUM, tags=['urgent'], no dueDate | Score = 28 (20 + 8) | Synonyms all work |
| 9 | Non-critical tag (no boost) | Priority=MEDIUM, tags=['work'], no dueDate | Score = 20 | Non-critical tags do not trigger boost |
| 10 | Recently updated | Priority=MEDIUM, updatedAt=1 min ago, no dueDate | Score = 25 (20 + 5) | Recent-update bonus |
| 11 | Not recently updated | Priority=MEDIUM, updatedAt=2 days ago, no dueDate | Score = 20 | No recent-update bonus |
| 12 | Combined: overdue + critical + urgent priority | Priority=URGENT, dueDate=yesterday, tags=['critical'] | Score = 78 (40 + 30 + 8) | Verifies all bonuses stack correctly |
| 13 | Unknown priority (defensive) | priority=999 (invalid) | Score = 0 + any modifiers | priorityWeights lookup returns undefined → `|| 0` |

### Priority of Test Cases

1. **P0 (must have):** 1 (baseline), 2 (overdue), 5 (completed), 12 (combined)
2. **P1 (important):** 3 (today), 4 (week), 7 (tags), 10 (recent update)
3. **P2 (edge cases):** 6 (review), 8 (urgent tag), 9 (non-critical tag), 11 (not recent), 13 (invalid priority)

---

## Part 1.2: Test Planning — All Three Functions

### calculateTaskScore

| Priority | Test | Type | Dependencies | Expected Outcome |
|----------|------|------|-------------|------------------|
| P0 | Score reflects base priority weight | Unit | Task with known priority | `urgent > high > medium > low` |
| P0 | Overdue adds 30 points | Unit | Task with past dueDate | `(priority*10) + 30` |
| P0 | DONE reduces score by 50 | Unit | Task with status DONE | `(priority*10) - 50` |
| P0 | Combined bonuses stack | Unit | Overdue + critical tag + URGENT | Sum of all modifiers |
| P1 | Due today adds 20 | Unit | Task with dueDate=today | `(priority*10) + 20` |
| P1 | Due in 1-2 days adds 15 | Unit | Task with dueDate=+1 day | `(priority*10) + 15` |
| P1 | Due in 3-7 days adds 10 | Unit | Task with dueDate=+5 days | `(priority*10) + 10` |
| P1 | Critical tag adds 8 | Unit | Task with tags=['critical'] | `(priority*10) + 8` |
| P1 | Recent update (< 1 day) adds 5 | Unit | Task updated 1 hour ago | `(priority*10) + 5` |
| P1 | REVIEW reduces by 15 | Unit | Task with status REVIEW | `(priority*10) - 15` |
| P2 | No due date → no bonus | Unit | Task without dueDate | `priority*10` |
| P2 | Non-critical tags → no bonus | Unit | Task with tags=['work'] | `priority*10` |
| P2 | No recent update → no bonus | Unit | Task updated 2 days ago | `priority*10` |
| P2 | Invalid priority defaults to 0 | Unit | Task with priority=999 | `0` (from `|| 0`) |
| P2 | Various tag spellings trigger boost | Unit | 'blocker', 'urgent', 'critical' | Each adds 8 |
| P2 | Blocked tag on edge | Unit | tags=['blocker'] | Score += 8 |

### sortTasksByImportance

| Priority | Test | Type | Dependencies | Expected Outcome |
|----------|------|------|-------------|------------------|
| P0 | Returns tasks sorted by score descending | Unit | 2+ tasks with different scores | Highest score first |
| P0 | Does not mutate original array | Unit | Original array reference | Same order after call |
| P1 | Empty array returns empty | Unit | `[]` | `[]` |
| P1 | Single task returns that task | Unit | `[task]` | `[task]` |
| P1 | Ties maintain relative order (stable?) | Unit | 2 tasks with same score | Order preserved (current sort is not guaranteed stable) |
| P2 | Large number of tasks performs correctly | Unit | 1000 tasks | All returned, sorted |

### getTopPriorityTasks

| Priority | Test | Type | Dependencies | Expected Outcome |
|----------|------|------|-------------|------------------|
| P0 | Returns top N tasks by score | Unit | 10 tasks, limit=3 | 3 tasks, highest scores |
| P0 | Uses default limit of 5 | Unit | 10 tasks, no limit arg | 5 tasks |
| P1 | Limit larger than array length | Unit | 3 tasks, limit=10 | All 3 tasks |
| P1 | Empty array returns empty | Unit | `[]`, limit=5 | `[]` |
| P1 | Limit of 0 returns empty | Unit | 5 tasks, limit=0 | `[]` |
| P2 | Limit of null/undefined uses default | Unit | 10 tasks, limit=null | 5 tasks |

---

## Test Dependencies

- **`calculateTaskScore`**: No dependencies — pure function taking a task object
- **`sortTasksByImportance`**: Depends on `calculateTaskScore` for each element
- **`getTopPriorityTasks`**: Depends on `sortTasksByImportance`

**Testing strategy**: Test `calculateTaskScore` exhaustively first (unit), then test `sortTasksByImportance` (relies on correctness of `calculateTaskScore` via mock or real), then `getTopPriorityTasks`.
