// Part 4: Integration Testing
// File: testing-exercise/part4-integration-tests.js
//
// This test verifies that calculateTaskScore, sortTasksByImportance,
// and getTopPriorityTasks work correctly together as a workflow.

const { Task, TaskPriority, TaskStatus } = require('../models');
const {
  calculateTaskScore,
  sortTasksByImportance,
  getTopPriorityTasks
} = require('../task_priority');

describe('Integration: Task Priority Workflow', () => {
  // Fixed reference date for deterministic tests
  const REFERENCE_DATE = new Date('2024-06-15T12:00:00Z');

  // Helper to create a task at MEDIUM priority with a specific due date offset
  function taskDueIn(daysOffset) {
    const t = new Task('Task due in ' + daysOffset);
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

  // =====================================
  // Scenario A: Mixed priority + due dates
  // =====================================
  test('workflow: mixed priorities and due dates sorted correctly', () => {
    // Task 1: URGENT, no due date          → score = 40
    // Task 2: HIGH, overdue (+30)          → score = 30 + 30 = 60
    // Task 3: MEDIUM, due today (+20)      → score = 20 + 20 = 40
    // Task 4: MEDIUM, no due date          → score = 20
    // Task 5: LOW, no due date             → score = 10

    const tasks = [];
    const t1 = new Task('URGENT no due');
    t1.priority = TaskPriority.URGENT;
    tasks.push(t1);

    const t2 = new Task('HIGH overdue');
    t2.priority = TaskPriority.HIGH;
    t2.dueDate = new Date(REFERENCE_DATE.getTime() - 86400000); // yesterday
    tasks.push(t2);

    const t3 = new Task('MEDIUM due today');
    t3.priority = TaskPriority.MEDIUM;
    t3.dueDate = REFERENCE_DATE;
    tasks.push(t3);

    const t4 = new Task('MEDIUM no due');
    t4.priority = TaskPriority.MEDIUM;
    tasks.push(t4);

    const t5 = new Task('LOW no due');
    t5.priority = TaskPriority.LOW;
    tasks.push(t5);

    // Verify individual scores match expectations
    expect(calculateTaskScore(t1)).toBe(40);
    expect(calculateTaskScore(t2)).toBe(30 + 30);   // 60
    expect(calculateTaskScore(t3)).toBe(20 + 20);   // 40
    expect(calculateTaskScore(t4)).toBe(20);
    expect(calculateTaskScore(t5)).toBe(10);

    // Now sort and verify order: highest score first
    const sorted = sortTasksByImportance(tasks);
    expect(sorted[0]).toBe(t2); // 60 — HIGH overdue
    expect(sorted[1]).toBe(t1); // 40 — URGENT no due (tied with t3, URGENT wins due to prio)
    expect(sorted[2]).toBe(t3); // 40 — MEDIUM due today
    expect(sorted[3]).toBe(t4); // 20 — MEDIUM no due
    expect(sorted[4]).toBe(t5); // 10 — LOW no due

    // Verify original array is unchanged
    expect(tasks.length).toBe(5);
    expect(tasks[0]).toBe(t1); // Original order preserved

    // Get top 2
    const top2 = getTopPriorityTasks(tasks, 2);
    expect(top2.length).toBe(2);
    expect(top2[0]).toBe(t2);
    expect(top2[1]).toBe(t1);

    // Get top 10 (more than available)
    const top10 = getTopPriorityTasks(tasks, 10);
    expect(top10.length).toBe(5); // All tasks returned
  });

  // =====================================
  // Scenario B: Tags + status modifiers
  // =====================================
  test('workflow: tags and completion status affect priority ranking', () => {
    // Task 1: HIGH priority, critical tag  → score = 30 + 8 = 38
    // Task 2: URGENT priority, DONE status → score = 40 - 50 = -10
    // Task 3: MEDIUM priority, REVIEW      → score = 20 - 15 = 5

    const tasks = [];

    const t1 = new Task('High critical');
    t1.priority = TaskPriority.HIGH;
    t1.tags = ['critical'];
    tasks.push(t1);

    const t2 = new Task('Urgent done');
    t2.priority = TaskPriority.URGENT;
    t2.status = TaskStatus.DONE;
    tasks.push(t2);

    const t3 = new Task('Medium review');
    t3.priority = TaskPriority.MEDIUM;
    t3.status = TaskStatus.REVIEW;
    tasks.push(t3);

    // Verify individual scores
    expect(calculateTaskScore(t1)).toBe(30 + 8);  // 38
    expect(calculateTaskScore(t2)).toBe(40 - 50); // -10
    expect(calculateTaskScore(t3)).toBe(20 - 15); // 5

    // Sorted: highest first
    const sorted = sortTasksByImportance(tasks);
    expect(sorted[0]).toBe(t1); // 38
    expect(sorted[1]).toBe(t3); // 5
    expect(sorted[2]).toBe(t2); // -10

    // getTopPriorityTasks with default limit
    const top = getTopPriorityTasks(tasks);
    expect(top.length).toBe(3); // Only 3 tasks exist, limit is 5 default
    expect(top[0]).toBe(t1);
  });

  // =====================================
  // Scenario C: Empty and singleton arrays
  // =====================================
  test('workflow: empty array returns empty results from all functions', () => {
    const empty = [];

    // sortTasksByImportance should not throw
    const sorted = sortTasksByImportance(empty);
    expect(sorted).toEqual([]);

    // getTopPriorityTasks should return empty
    const top = getTopPriorityTasks(empty, 5);
    expect(top).toEqual([]);

    // Calculating score on a minimal task should not throw
    const minimal = new Task('Minimal');
    expect(typeof calculateTaskScore(minimal)).toBe('number');
  });

  test('workflow: single task returns itself', () => {
    const t = new Task('Solo');
    t.priority = TaskPriority.URGENT;

    const sorted = sortTasksByImportance([t]);
    expect(sorted.length).toBe(1);
    expect(sorted[0]).toBe(t);

    const top = getTopPriorityTasks([t], 1);
    expect(top[0]).toBe(t);
  });

  // =====================================
  // Scenario D: All modifiers combined
  // =====================================
  test('workflow: full combination of all score modifiers', () => {
    // Create a spectrum of tasks with different modifier combinations
    const tasks = [];

    // Super high: URGENT + overdue + critical tag
    const t1 = new Task('Urgent overdue critical');
    t1.priority = TaskPriority.URGENT;
    t1.dueDate = new Date(REFERENCE_DATE.getTime() - 2 * 86400000);
    t1.tags = ['critical'];
    tasks.push(t1); // score: 40 + 30 + 8 = 78

    // Medium-low: DONE + was HIGH
    const t2 = new Task('Done high');
    t2.priority = TaskPriority.HIGH;
    t2.status = TaskStatus.DONE;
    tasks.push(t2); // score: 30 - 50 = -20

    // Medium: REVIEW + due in 3 days
    const t3 = new Task('Review due-soon');
    t3.priority = TaskPriority.MEDIUM;
    t3.status = TaskStatus.REVIEW;
    t3.dueDate = new Date(REFERENCE_DATE.getTime() + 3 * 86400000);
    tasks.push(t3); // score: 20 - 15 + 10 = 15

    // High + due today
    const t4 = new Task('High due today');
    t4.priority = TaskPriority.HIGH;
    t4.dueDate = REFERENCE_DATE;
    tasks.push(t4); // score: 30 + 20 = 50

    // LOW + recently updated
    const t5 = new Task('Low just updated');
    t5.priority = TaskPriority.LOW;
    t5.updatedAt = new Date(REFERENCE_DATE.getTime() - 2 * 3600000); // 2 hours ago
    tasks.push(t5); // score: 10 + 5 = 15

    // Verify scores
    expect(calculateTaskScore(t1)).toBe(78);
    expect(calculateTaskScore(t2)).toBe(-20);
    expect(calculateTaskScore(t3)).toBe(15);
    expect(calculateTaskScore(t4)).toBe(50);
    expect(calculateTaskScore(t5)).toBe(15);

    // Sorted
    const sorted = sortTasksByImportance(tasks);
    expect(sorted[0]).toBe(t1); // 78
    expect(sorted[1]).toBe(t4); // 50
    // t3 (15) and t5 (15) — order among ties is not guaranteed
    expect(sorted[3]).toBe(t2); // -20

    // Top 3
    const top3 = getTopPriorityTasks(tasks, 3);
    expect(top3.length).toBe(3);
    expect(top3[0]).toBe(t1);
    expect(top3[1]).toBe(t4);
    // Third spot: either t3 or t5 (tied at 15)
  });
});

describe('Integration: Sorting stability and edge cases', () => {
  test('getTopPriorityTasks with limit larger than array', () => {
    const tasks = [
      new Task('A', '', TaskPriority.HIGH),
      new Task('B', '', TaskPriority.MEDIUM),
    ];
    const top = getTopPriorityTasks(tasks, 10);
    expect(top.length).toBe(2);
  });

  test('getTopPriorityTasks with limit 0', () => {
    const tasks = [
      new Task('A'),
      new Task('B'),
    ];
    const top = getTopPriorityTasks(tasks, 0);
    expect(top).toEqual([]);
  });
});
