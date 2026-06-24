# Exercise 2: Algorithm Deconstruction Challenge

## Algorithm 1: Task Priority Scoring (`task_priority.js`)

### `calculateTaskScore(task)`
Computes a numeric score used to sort tasks by importance.

**Logic:**
1. **Base score:** priority weight × 10 (LOW=1, MEDIUM=2, HIGH=3, URGENT=4)
2. **Due date bonus:** overdue→+30, due today→+20, due in 2 days→+15, due in a week→+10
3. **Status penalty:** DONE→−50, REVIEW→−15
4. **Tag boost:** tasks tagged "blocker", "critical", or "urgent"→+8
5. **Recent update boost:** updated in last 24h→+5

### `sortTasksByImportance(tasks)`
Returns a new array sorted by score descending (most important first). Does not mutate the original.

### `getTopPriorityTasks(tasks, limit=5)`
Returns the top N tasks by importance score.

## Algorithm 2: Task Parser (`task_parser.js`)

### `parseTaskFromText(text)`
Parses free-form text into a Task object using markers:
- `!N` or `!name` → priority (1-4 or low/medium/high/urgent)
- `@tag` → tags
- `#date` → due date (today, tomorrow, next_week, day names, YYYY-MM-DD)

### `getNextWeekday(currentDate, targetDay)`
Finds the next occurrence of a specific weekday (0=Sunday, 1=Monday, etc.). If today is the target day, returns next week.

## Algorithm 3: Task List Merge (`task_list_merge.js`)

### `mergeTaskLists(localTasks, remoteTasks)`
Merges two task dictionaries with conflict resolution. Returns:
- `mergedTasks` — combined task set
- `toCreateRemote` — tasks to create on remote
- `toUpdateRemote` — tasks to update on remote
- `toCreateLocal` — tasks to create locally
- `toUpdateLocal` — tasks to update locally

### `resolveTaskConflict(localTask, remoteTask)`
Resolution rules:
1. Most recent `updatedAt` wins for title, description, priority, dueDate
2. DONE status overrides not-done (completed wins)
3. Tags are merged as a union from both sources
4. Timestamp is set to the latest of the two

### `arraysEqual(a, b)`
Compares two arrays regardless of order (sorted comparison).
