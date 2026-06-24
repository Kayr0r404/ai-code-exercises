# Part 2: Improving a Single Test

## Exercise 2.1: From Simple to Robust

### Initial simple test

```js
test('calculateTaskScore should give higher score to urgent tasks', () => {
  const low = new Task('Low'); low.priority = TaskPriority.LOW;
  const urgent = new Task('Urgent'); urgent.priority = TaskPriority.URGENT;
  expect(calculateTaskScore(urgent)).toBeGreaterThan(calculateTaskScore(low));
});
```

### Improved test

```js
describe('calculateTaskScore', () => {
  // Baseline — verifies the function works with minimum input
  test('baseline score for medium priority with no modifiers', () => {
    const task = new Task('Default task');
    expect(calculateTaskScore(task)).toBe(20); // MEDIUM=2, 2*10=20
  });

  // Priority weights — exact values, not just relative comparison
  test('priority weight is reflected in base score', () => {
    const makeTask = (priority) => {
      const t = new Task('test');
      t.priority = priority;
      return t;
    };

    const pairs = [
      { priority: TaskPriority.LOW, expected: 10 },    // 1*10
      { priority: TaskPriority.MEDIUM, expected: 20 },  // 2*10
      { priority: TaskPriority.HIGH, expected: 30 },    // 3*10
      { priority: TaskPriority.URGENT, expected: 40 },  // 4*10
    ];

    for (const { priority, expected } of pairs) {
      expect(calculateTaskScore(makeTask(priority))).toBe(expected);
    }
  });

  // Due date scoring — tests the exact bonus amounts
  describe('due date bonuses', () => {
    // We use a fixed reference date so the tests don't depend on "now"
    const REFERENCE_DATE = new Date('2024-06-15T12:00:00Z');

    function makeTaskDueDaysFromNow(daysDelta) {
      const t = new Task('test');
      t.priority = TaskPriority.MEDIUM;
      const due = new Date(REFERENCE_DATE);
      due.setDate(due.getDate() + daysDelta);
      t.dueDate = due;
      return t;
    }

    test('overdue adds 30', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = makeTaskDueDaysFromNow(-1);
      expect(calculateTaskScore(task)).toBe(20 + 30);
      jest.useRealTimers();
    });

    test('due today adds 20', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = makeTaskDueDaysFromNow(0);
      expect(calculateTaskScore(task)).toBe(20 + 20);
      jest.useRealTimers();
    });

    test('due within 2 days adds 15', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = makeTaskDueDaysFromNow(1);
      expect(calculateTaskScore(task)).toBe(20 + 15);
      jest.useRealTimers();
    });

    test('due within 7 days adds 10', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = makeTaskDueDaysFromNow(5);
      expect(calculateTaskScore(task)).toBe(20 + 10);
      jest.useRealTimers();
    });

    test('due more than 7 days out adds no bonus', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = makeTaskDueDaysFromNow(10);
      expect(calculateTaskScore(task)).toBe(20);
      jest.useRealTimers();
    });

    test('no due date adds no bonus', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      expect(calculateTaskScore(task)).toBe(20);
    });
  });

  // Status penalties
  describe('status penalties', () => {
    test('DONE reduces score by 50', () => {
      const task = new Task('test');
      task.priority = TaskPriority.URGENT; // score 40
      task.status = TaskStatus.DONE;
      expect(calculateTaskScore(task)).toBe(40 - 50); // -10
    });

    test('REVIEW reduces score by 15', () => {
      const task = new Task('test');
      task.priority = TaskPriority.HIGH; // score 30
      task.status = TaskStatus.REVIEW;
      expect(calculateTaskScore(task)).toBe(30 - 15); // 15
    });
  });

  // Tag bonuses
  describe('tag bonuses', () => {
    test('critical tag adds 8', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.tags = ['critical'];
      expect(calculateTaskScore(task)).toBe(20 + 8);
    });

    test('urgent tag adds 8', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.tags = ['urgent'];
      expect(calculateTaskScore(task)).toBe(20 + 8);
    });

    test('blocker tag adds 8', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.tags = ['blocker'];
      expect(calculateTaskScore(task)).toBe(20 + 8);
    });

    test('non-critical tags do not add bonus', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.tags = ['work', 'frontend'];
      expect(calculateTaskScore(task)).toBe(20);
    });

    test('multiple matching tags still add 8 once', () => {
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.tags = ['critical', 'urgent', 'blocker'];
      // Code uses `some(...)` so it's a boolean — +8 once
      expect(calculateTaskScore(task)).toBe(20 + 8);
    });
  });

  // Recent update bonus
  describe('recent update bonus', () => {
    const REFERENCE_DATE = new Date('2024-06-15T12:00:00Z');

    test('task updated within last day gets +5', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.updatedAt = new Date(REFERENCE_DATE.getTime() - 1 * 60 * 60 * 1000); // 1 hour ago
      expect(calculateTaskScore(task)).toBe(20 + 5);
      jest.useRealTimers();
    });

    test('task updated more than 1 day ago does not get bonus', () => {
      jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
      const task = new Task('test');
      task.priority = TaskPriority.MEDIUM;
      task.updatedAt = new Date(REFERENCE_DATE.getTime() - 2 * 24 * 60 * 60 * 1000); // 2 days ago
      expect(calculateTaskScore(task)).toBe(20);
      jest.useRealTimers();
    });
  });
});
```

### Key improvements

| Aspect | Simple Test | Improved Test |
|--------|------------|---------------|
| Assertions | Relative (`toBeGreaterThan`) | Absolute (`toBe`) |
| Edge cases | None | Empty tags, no dueDate, each bonus bracket |
| Time dependency | `new Date()` — nondeterministic | `jest.useFakeTimers` with fixed reference date |
| Organization | One flat test | Grouped by behavior (dueDate, status, tags, recency) |
| Coverage | 1 behavior | 8 behaviors across all code paths |

---

## Exercise 2.2: Due Date Calculation — Comprehensive Tests

### Pseudocode (initial idea)

```
test('overdue tasks get higher score')
  create task with yesterday as dueDate
  calculate score
  assert score is higher than a task due tomorrow
```

### Comprehensive test — with fixed time and exact assertions

```js
describe('due date calculation', () => {
  const REFERENCE_DATE = new Date('2024-06-15T12:00:00Z');
  const MEDIUM_BASE = 20;

  // Helper: create a task with MEDIUM priority and a specific due date offset
  function taskDueIn(daysOffset) {
    const t = new Task('test');
    t.priority = TaskPriority.MEDIUM;
    const due = new Date(REFERENCE_DATE);
    due.setDate(due.getDate() + daysOffset);
    t.dueDate = due;
    return t;
  }

  beforeEach(() => {
    jest.useFakeTimers().setSystemTime(REFERENCE_DATE);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('overdue: daysUntilDue < 0 → +30', () => {
    // Yesterday
    expect(calculateTaskScore(taskDueIn(-1))).toBe(MEDIUM_BASE + 30);
    // A week ago (still overdue)
    expect(calculateTaskScore(taskDueIn(-7))).toBe(MEDIUM_BASE + 30);
  });

  test('due today: daysUntilDue === 0 → +20', () => {
    expect(calculateTaskScore(taskDueIn(0))).toBe(MEDIUM_BASE + 20);
  });

  test('due within 2 days: daysUntilDue 1..2 → +15', () => {
    expect(calculateTaskScore(taskDueIn(1))).toBe(MEDIUM_BASE + 15);
    expect(calculateTaskScore(taskDueIn(2))).toBe(MEDIUM_BASE + 15);
  });

  test('due within 7 days: daysUntilDue 3..7 → +10', () => {
    expect(calculateTaskScore(taskDueIn(3))).toBe(MEDIUM_BASE + 10);
    expect(calculateTaskScore(taskDueIn(7))).toBe(MEDIUM_BASE + 10);
  });

  test('due more than 7 days away: daysUntilDue > 7 → +0', () => {
    expect(calculateTaskScore(taskDueIn(8))).toBe(MEDIUM_BASE);
    expect(calculateTaskScore(taskDueIn(365))).toBe(MEDIUM_BASE);
  });

  test('no dueDate → no bonus, no error', () => {
    const t = new Task('test');
    t.priority = TaskPriority.MEDIUM;
    expect(calculateTaskScore(t)).toBe(MEDIUM_BASE);
  });

  test('boundary: exactly midnight before due day', () => {
    // Due at 00:00:000 today → daysUntilDue = 0 (today bonus)
    const dueMidnight = new Date(REFERENCE_DATE);
    dueMidnight.setHours(0, 0, 0, 0);
    const t = new Task('test');
    t.priority = TaskPriority.MEDIUM;
    t.dueDate = dueMidnight;
    expect(calculateTaskScore(t)).toBe(MEDIUM_BASE + 20);
  });

  test('combined: overdue + urgent priority', () => {
    const t = taskDueIn(-1);
    t.priority = TaskPriority.URGENT; // 40
    expect(calculateTaskScore(t)).toBe(40 + 30); // 70
  });

  test('combined: overdue + done status', () => {
    const t = taskDueIn(-1);
    t.priority = TaskPriority.URGENT; // 40
    t.status = TaskStatus.DONE;       // -50
    expect(calculateTaskScore(t)).toBe(40 + 30 - 50); // 20
  });
});
```

### Why this is better

1. **Deterministic** — `jest.useFakeTimers` with a fixed date eliminates flakiness from `new Date()` calls inside the function
2. **Exact assertions** — uses `.toBe(N)` instead of `.toBeGreaterThan()` so any change to the scoring formula is immediately visible
3. **Boundary coverage** — tests each `if/else if` bracket explicitly, including edge values (day 0, day 2, day 7, day 8)
4. **Null case** — verifies no exception when `dueDate` is null
5. **Combination tests** — verifies due date bonus stacks correctly with priority and status modifiers
