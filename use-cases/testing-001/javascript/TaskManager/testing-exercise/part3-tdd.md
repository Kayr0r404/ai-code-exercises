# Part 3: Test-Driven Development Practice

## Exercise 3.1: TDD for a New Feature

**Feature:** Tasks assigned to the current user should get a score boost of +12.

### Step 1: Write a failing test

```js
describe('TDD new feature — assigned user score boost', () => {
  // The current user context — we'll need to inject this somehow.
  // For now, we test the concept: if currentUserId matches task.assignedTo,
  // the score gets +12.

  test('task assigned to current user gets +12 score boost', () => {
    const task = new Task('My task');
    task.priority = TaskPriority.MEDIUM;
    task.assignedTo = 'user-abc-123';

    // This test will fail because calculateTaskScore doesn't know about
    // the current user yet. We'll need to pass context or use a module-level
    // setting.
    const score = calculateTaskScore(task, { currentUserId: 'user-abc-123' });
    expect(score).toBe(20 + 12);
  });

  test('task assigned to another user does not get boost', () => {
    const task = new Task('Other task');
    task.priority = TaskPriority.MEDIUM;
    task.assignedTo = 'user-xyz-789';

    const score = calculateTaskScore(task, { currentUserId: 'user-abc-123' });
    expect(score).toBe(20);
  });

  test('task with no assigned user does not get boost', () => {
    const task = new Task('Unassigned task');
    task.priority = TaskPriority.MEDIUM;

    const score = calculateTaskScore(task, { currentUserId: 'user-abc-123' });
    expect(score).toBe(20);
  });
});
```

### Step 2: Implement minimal code to make it pass

Add to `task_priority.js`:

```js
function calculateTaskScore(task, context = {}) {
  // ... existing code ...

  // Boost for tasks assigned to the current user
  if (context.currentUserId && task.assignedTo === context.currentUserId) {
    score += 12;
  }

  return score;
}
```

Also need to add `assignedTo` field to the `Task` model in `models.js`:

```js
class Task {
  constructor(title, description = '', priority = TaskPriority.MEDIUM, dueDate = null, tags = []) {
    // ... existing fields ...
    this.assignedTo = null; // NEW
  }
}
```

Update the `Task` constructor and default properties. Since `assignedTo` is null by default, existing tasks are unaffected.

### Step 3: All tests pass after implementation

The first test now passes because:
- `context.currentUserId` is set
- `task.assignedTo` matches
- `score` starts at 20 (MEDIUM) and gets +12

### Step 4: Write the next test

```js
test('boost stacks with other score modifiers', () => {
  const task = new Task('Combined');
  task.priority = TaskPriority.URGENT; // 40
  task.assignedTo = 'user-abc-123';
  task.tags = ['critical']; // +8

  const score = calculateTaskScore(task, { currentUserId: 'user-abc-123' });
  expect(score).toBe(40 + 8 + 12); // 60
});

test('no context passed → no crash, no boost', () => {
  const task = new Task('No context');
  task.priority = TaskPriority.MEDIUM;
  task.assignedTo = 'user-abc-123';

  expect(calculateTaskScore(task)).toBe(20);
});
```

### Step 5: Refactor

The `context` parameter is clean enough. We could later extract the current user into a module-level setting if many functions need it, but for now a parameter is fine. No refactoring needed.

---

## Exercise 3.2: TDD for Bug Fix

**Bug:** The "days since update" calculation uses `Math.floor((now - updatedAt) / (1000 * 60 * 60 * 24))` which gives a fractional-day result truncated downward. A task updated 23 hours ago has `daysSinceUpdate = 0` and gets the +5 bonus, even though it was actually yesterday.

**Expected behavior:** The calculation should compare date-only values (strip the time component), so "yesterday at 3 PM" counts as 1 day ago, regardless of the time of day.

### Step 1: Write a test that demonstrates the bug

```js
describe('TDD bug fix — days since update', () => {
  const REFERENCE_DATE = new Date('2024-06-15T12:00:00Z');

  beforeEach(() => {
    jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('task updated yesterday should NOT get recent update bonus', () => {
    const task = new Task('test');
    task.priority = TaskPriority.MEDIUM;

    // Updated yesterday at 1 PM (23 hours ago — still < 24h in current code)
    task.updatedAt = new Date('2024-06-14T13:00:00Z');

    // BUG: current code: floor((2024-06-15T12:00 - 2024-06-14T13:00) / 86400000)
    //                    = floor(23h / 24h) = floor(0.958) = 0
    //                    → daysSinceUpdate < 1 → +5 bonus (WRONG — it was yesterday)
    //
    // FIXED code should use date-only comparison:
    //                    today=2024-06-15, updatedDate=2024-06-14
    //                    diff = 1 day → no bonus

    const score = calculateTaskScore(task);
    expect(score).toBe(20); // No +5 — it was updated yesterday
  });

  test('task updated today should still get the bonus', () => {
    const task = new Task('test');
    task.priority = TaskPriority.MEDIUM;

    // Updated 1 hour ago — same calendar day
    task.updatedAt = new Date('2024-06-15T11:00:00Z');

    const score = calculateTaskScore(task);
    expect(score).toBe(20 + 5); // Should still get bonus
  });

  test('task updated exactly 24 hours ago but on different calendar day', () => {
    const task = new Task('test');
    task.priority = TaskPriority.MEDIUM;

    // Updated at midnight yesterday → 24h ago, but different date
    // Current code: floor(24h / 24h) = floor(1.0) = 1 → no bonus
    // This behavior should be preserved
    task.updatedAt = new Date('2024-06-14T12:00:00Z');

    const score = calculateTaskScore(task);
    expect(score).toBe(20); // No bonus — different day
  });
});
```

### Step 2: Run the test — it fails

The first test fails as expected:
- Task updated at 2024-06-14T13:00, now is 2024-06-15T12:00
- `now - updatedAt` = 23 hours = 82,800,000 ms
- `/ (1000 * 60 * 60 * 24)` = 0.958
- `Math.floor(0.958)` = 0
- `0 < 1` → true → +5 bonus applied
- **Test expects 20, gets 25** → FAIL

### Step 3: Fix the code

Replace the time-based calculation with a date-only comparison in `task_priority.js`:

```js
// Boost score for recently updated tasks
const now = new Date();
const updatedAt = new Date(task.updatedAt);

// Compare dates only (strip time components)
const nowDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
const updatedDate = new Date(updatedAt.getFullYear(), updatedAt.getMonth(), updatedAt.getDate());
const daysSinceUpdate = Math.floor((nowDate - updatedDate) / (1000 * 60 * 60 * 24));

if (daysSinceUpdate < 1) {
  score += 5;
}
```

### Step 4: Run the tests — all pass

- Task updated yesterday at 1 PM: `nowDate - updatedDate` = 1 day → `daysSinceUpdate = 1` → no bonus ✓
- Task updated 1 hour ago: `nowDate - updatedDate` = 0 days → `daysSinceUpdate = 0` → +5 bonus ✓
- Task updated exactly 24h ago at same time: `nowDate - updatedDate` = 1 day → no bonus ✓

### Step 5: Regression check

Run the full test suite to ensure nothing else broke. The existing test "should boost score for recently updated tasks" still passes because it tests relative comparison (recent > not recent), not absolute values.
