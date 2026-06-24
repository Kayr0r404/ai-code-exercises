const { Task, TaskPriority } = require('../models');
const { parseTaskFromText } = require('../task_parser');

describe('Task Parser', () => {
  describe('parseTaskFromText', () => {
    test('should parse basic task title', () => {
      const task = parseTaskFromText('Buy milk');

      expect(task).toBeInstanceOf(Task);
      expect(task.title).toBe('Buy milk');
      expect(task.priority).toBe(TaskPriority.MEDIUM);
      expect(task.dueDate).toBeNull();
      expect(task.tags).toEqual([]);
    });

    test('should parse task with priority', () => {
      const tests = [
        { text: 'Buy milk !1', expected: TaskPriority.LOW },
        { text: 'Buy milk !low', expected: TaskPriority.LOW },
        { text: 'Buy milk !3', expected: TaskPriority.HIGH },
        { text: 'Buy milk !urgent', expected: TaskPriority.URGENT }
      ];

      for (const { text, expected } of tests) {
        const task = parseTaskFromText(text);
        expect(task.title).toBe('Buy milk');
        expect(task.priority).toBe(expected);
      }
    });

    test('should parse task with tags', () => {
      const task = parseTaskFromText('Buy milk @shopping @groceries');

      expect(task.title).toBe('Buy milk');
      expect(task.tags).toContain('shopping');
      expect(task.tags).toContain('groceries');
      expect(task.tags.length).toBe(2);
    });

    test('should parse task with date markers', () => {
      const mockDate = new Date('2023-06-15');
      jest.spyOn(global, 'Date').mockImplementation(() => mockDate);

      const task = parseTaskFromText('Buy milk #tomorrow');

      expect(task.title).toBe('Buy milk');
      expect(task.dueDate).toEqual(new Date('2023-06-16'));

      jest.restoreAllMocks();
    });

    test('should handle whitespace correctly', () => {
      const task = parseTaskFromText('  Buy   milk   @shopping   !high  ');

      expect(task.title).toBe('Buy milk');
      expect(task.priority).toBe(TaskPriority.HIGH);
      expect(task.tags).toContain('shopping');
    });
  });
});
