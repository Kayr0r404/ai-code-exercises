const { Task, TaskPriority, TaskStatus } = require('../models');
const { calculateTaskScore, sortTasksByImportance, getTopPriorityTasks } = require('../task_priority');

describe('Task Priority', () => {
  describe('calculateTaskScore', () => {
    test('should calculate score based on priority', () => {
      const low = new Task('Low'); low.priority = TaskPriority.LOW;
      const high = new Task('High'); high.priority = TaskPriority.HIGH;
      const urgent = new Task('Urgent'); urgent.priority = TaskPriority.URGENT;

      expect(calculateTaskScore(low)).toBeLessThan(calculateTaskScore(high));
      expect(calculateTaskScore(high)).toBeLessThan(calculateTaskScore(urgent));
    });

    test('should increase score for tasks due soon', () => {
      const today = new Date();
      const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1);
      const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);

      const overdueScore = calculateTaskScore(new Task('Overdue', '', TaskPriority.MEDIUM, yesterday));
      const todayScore = calculateTaskScore(new Task('Today', '', TaskPriority.MEDIUM, today));
      const tomorrowScore = calculateTaskScore(new Task('Tomorrow', '', TaskPriority.MEDIUM, tomorrow));

      expect(overdueScore).toBeGreaterThan(todayScore);
      expect(todayScore).toBeGreaterThan(tomorrowScore);
    });

    test('should reduce score for completed tasks', () => {
      const todo = new Task('Todo');
      const done = new Task('Done'); done.status = TaskStatus.DONE;

      expect(calculateTaskScore(done)).toBeLessThan(calculateTaskScore(todo));
    });

    test('should boost score for tasks with critical tags', () => {
      const regular = new Task('Regular');
      const critical = new Task('Critical'); critical.tags = ['critical'];

      expect(calculateTaskScore(critical)).toBeGreaterThan(calculateTaskScore(regular));
    });
  });

  describe('sortTasksByImportance', () => {
    test('should sort tasks by score descending', () => {
      const low = new Task('Low'); low.priority = TaskPriority.LOW;
      const urgent = new Task('Urgent'); urgent.priority = TaskPriority.URGENT;
      const tasks = [low, urgent];

      const sorted = sortTasksByImportance(tasks);

      expect(sorted[0]).toBe(urgent);
      expect(sorted[1]).toBe(low);
    });

    test('should not modify the original array', () => {
      const tasks = [new Task('A'), new Task('B')];
      const copy = [...tasks];

      sortTasksByImportance(tasks);

      expect(tasks).toEqual(copy);
    });
  });

  describe('getTopPriorityTasks', () => {
    test('should return top N tasks', () => {
      const tasks = [
        new Task('1', '', TaskPriority.LOW),
        new Task('2', '', TaskPriority.HIGH),
        new Task('3', '', TaskPriority.URGENT)
      ];

      const top = getTopPriorityTasks(tasks, 2);

      expect(top.length).toBe(2);
    });

    test('should use default limit of 5', () => {
      const tasks = Array.from({ length: 10 }, (_, i) => new Task(`Task ${i}`));
      expect(getTopPriorityTasks(tasks).length).toBe(5);
    });
  });
});
