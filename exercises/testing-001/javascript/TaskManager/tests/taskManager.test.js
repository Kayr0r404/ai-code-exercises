const { TaskManager } = require('../app');
const { TaskStorage } = require('../storage');
const { Task, TaskPriority, TaskStatus } = require('../models');

jest.mock('../storage', () => {
  return {
    TaskStorage: jest.fn().mockImplementation(() => {
      return {
        addTask: jest.fn().mockImplementation(task => task.id),
        getTask: jest.fn(),
        updateTask: jest.fn().mockReturnValue(true),
        deleteTask: jest.fn().mockReturnValue(true),
        getAllTasks: jest.fn().mockReturnValue([]),
        getTasksByStatus: jest.fn().mockReturnValue([]),
        getTasksByPriority: jest.fn().mockReturnValue([]),
        getOverdueTasks: jest.fn().mockReturnValue([]),
        save: jest.fn()
      };
    })
  };
});

describe('TaskManager', () => {
  let taskManager;

  beforeEach(() => {
    jest.clearAllMocks();
    taskManager = new TaskManager('test-tasks.json');
  });

  describe('constructor', () => {
    test('should initialize with custom storage path', () => {
      expect(TaskStorage).toHaveBeenCalledWith('test-tasks.json');
    });
  });

  describe('createTask', () => {
    test('should create a task with minimal information', () => {
      const taskId = taskManager.createTask('Test Task');

      expect(taskManager.storage.addTask).toHaveBeenCalled();
      expect(taskId).toBeDefined();
    });

    test('should create a task with all information', () => {
      const taskId = taskManager.createTask('Test Task', 'Description', TaskPriority.HIGH, '2023-12-31', ['test']);

      expect(taskManager.storage.addTask).toHaveBeenCalled();
      expect(taskId).toBeDefined();
    });

    test('should return null for invalid date', () => {
      const taskId = taskManager.createTask('Test Task', '', 2, 'invalid-date');

      expect(taskManager.storage.addTask).not.toHaveBeenCalled();
      expect(taskId).toBeNull();
    });
  });

  describe('listTasks', () => {
    test('should return all tasks when no filters are provided', () => {
      taskManager.listTasks();
      expect(taskManager.storage.getAllTasks).toHaveBeenCalled();
    });

    test('should return overdue tasks when showOverdue is true', () => {
      taskManager.listTasks(null, null, true);
      expect(taskManager.storage.getOverdueTasks).toHaveBeenCalled();
    });

    test('should return tasks filtered by status', () => {
      taskManager.listTasks(TaskStatus.TODO);
      expect(taskManager.storage.getTasksByStatus).toHaveBeenCalledWith(TaskStatus.TODO);
    });

    test('should return tasks filtered by priority', () => {
      taskManager.listTasks(null, TaskPriority.HIGH);
      expect(taskManager.storage.getTasksByPriority).toHaveBeenCalledWith(TaskPriority.HIGH);
    });
  });

  describe('updateTaskStatus', () => {
    test('should update task status to non-done status', () => {
      const result = taskManager.updateTaskStatus('task-id', TaskStatus.IN_PROGRESS);

      expect(taskManager.storage.updateTask).toHaveBeenCalledWith('task-id', { status: TaskStatus.IN_PROGRESS });
      expect(result).toBe(true);
    });

    test('should mark task as done when status is DONE', () => {
      const mockTask = { markAsDone: jest.fn() };
      taskManager.storage.getTask.mockReturnValueOnce(mockTask);

      const result = taskManager.updateTaskStatus('task-id', TaskStatus.DONE);

      expect(mockTask.markAsDone).toHaveBeenCalled();
      expect(taskManager.storage.save).toHaveBeenCalled();
      expect(result).toBe(true);
    });

    test('should return false when task is not found', () => {
      taskManager.storage.getTask.mockReturnValueOnce(null);

      expect(taskManager.updateTaskStatus('non-existent', TaskStatus.DONE)).toBe(false);
    });
  });

  describe('updateTaskPriority', () => {
    test('should update task priority', () => {
      const result = taskManager.updateTaskPriority('task-id', TaskPriority.HIGH);

      expect(taskManager.storage.updateTask).toHaveBeenCalledWith('task-id', { priority: TaskPriority.HIGH });
      expect(result).toBe(true);
    });
  });

  describe('updateTaskDueDate', () => {
    test('should update task due date with valid date', () => {
      const result = taskManager.updateTaskDueDate('task-id', '2023-12-31');

      expect(taskManager.storage.updateTask).toHaveBeenCalled();
      expect(result).toBe(true);
    });

    test('should return false for invalid date', () => {
      const result = taskManager.updateTaskDueDate('task-id', 'invalid-date');

      expect(taskManager.storage.updateTask).not.toHaveBeenCalled();
      expect(result).toBe(false);
    });
  });

  describe('deleteTask', () => {
    test('should delete a task', () => {
      expect(taskManager.deleteTask('task-id')).toBe(true);
      expect(taskManager.storage.deleteTask).toHaveBeenCalledWith('task-id');
    });
  });

  describe('getTaskDetails', () => {
    test('should return task details', () => {
      const mockTask = { id: 'task-id', title: 'Test Task' };
      taskManager.storage.getTask.mockReturnValueOnce(mockTask);

      expect(taskManager.getTaskDetails('task-id')).toEqual(mockTask);
    });
  });

  describe('addTagToTask', () => {
    test('should add a tag to a task', () => {
      const mockTask = { tags: ['existing'] };
      taskManager.storage.getTask.mockReturnValueOnce(mockTask);

      const result = taskManager.addTagToTask('task-id', 'new-tag');

      expect(mockTask.tags).toContain('new-tag');
      expect(taskManager.storage.save).toHaveBeenCalled();
      expect(result).toBe(true);
    });

    test('should not add duplicate tag', () => {
      const mockTask = { tags: ['tag'] };
      taskManager.storage.getTask.mockReturnValueOnce(mockTask);

      const result = taskManager.addTagToTask('task-id', 'tag');

      expect(mockTask.tags).toEqual(['tag']);
      expect(taskManager.storage.save).not.toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('removeTagFromTask', () => {
    test('should remove a tag from a task', () => {
      const mockTask = { tags: ['tag1', 'tag2'] };
      taskManager.storage.getTask.mockReturnValueOnce(mockTask);

      const result = taskManager.removeTagFromTask('task-id', 'tag1');

      expect(mockTask.tags).toEqual(['tag2']);
      expect(taskManager.storage.save).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('getStatistics', () => {
    test('should return task statistics', () => {
      const mockTasks = [
        { status: TaskStatus.TODO, priority: TaskPriority.LOW, isOverdue: () => false, completedAt: null },
        { status: TaskStatus.IN_PROGRESS, priority: TaskPriority.MEDIUM, isOverdue: () => true, completedAt: null },
        { status: TaskStatus.DONE, priority: TaskPriority.HIGH, isOverdue: () => false, completedAt: new Date() }
      ];

      taskManager.storage.getAllTasks.mockReturnValueOnce(mockTasks);

      const stats = taskManager.getStatistics();

      expect(stats.total).toBe(3);
      expect(stats.byStatus[TaskStatus.TODO]).toBe(1);
      expect(stats.byStatus[TaskStatus.IN_PROGRESS]).toBe(1);
      expect(stats.byStatus[TaskStatus.DONE]).toBe(1);
      expect(stats.byPriority[TaskPriority.LOW]).toBe(1);
      expect(stats.byPriority[TaskPriority.MEDIUM]).toBe(1);
      expect(stats.byPriority[TaskPriority.HIGH]).toBe(1);
    });
  });
});
