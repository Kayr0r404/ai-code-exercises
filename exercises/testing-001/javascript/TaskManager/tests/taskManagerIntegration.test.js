const fs = require('fs');
const { TaskManager } = require('../app');
const { TaskStatus, TaskPriority } = require('../models');

describe('TaskManager Integration', () => {
  const TEST_STORAGE_PATH = 'test-integration-tasks.json';
  let taskManager;

  beforeEach(() => {
    taskManager = new TaskManager(TEST_STORAGE_PATH);
    if (fs.existsSync(TEST_STORAGE_PATH)) {
      fs.unlinkSync(TEST_STORAGE_PATH);
    }
  });

  afterEach(() => {
    if (fs.existsSync(TEST_STORAGE_PATH)) {
      fs.unlinkSync(TEST_STORAGE_PATH);
    }
  });

  test('should create and retrieve a task', () => {
    const taskId = taskManager.createTask('Integration Test', 'Desc', TaskPriority.HIGH, '2023-12-31', ['test']);

    expect(taskId).toBeDefined();

    const task = taskManager.getTaskDetails(taskId);
    expect(task.title).toBe('Integration Test');
    expect(task.description).toBe('Desc');
    expect(task.priority).toBe(TaskPriority.HIGH);
    expect(task.tags).toEqual(['test']);

    expect(fs.existsSync(TEST_STORAGE_PATH)).toBe(true);
  });

  test('should update task status', () => {
    const taskId = taskManager.createTask('Status Test');

    expect(taskManager.updateTaskStatus(taskId, TaskStatus.IN_PROGRESS)).toBe(true);
    expect(taskManager.getTaskDetails(taskId).status).toBe(TaskStatus.IN_PROGRESS);
  });

  test('should update task priority', () => {
    const taskId = taskManager.createTask('Priority Test');

    expect(taskManager.updateTaskPriority(taskId, TaskPriority.HIGH)).toBe(true);
    expect(taskManager.getTaskDetails(taskId).priority).toBe(TaskPriority.HIGH);
  });

  test('should add and remove tags', () => {
    const taskId = taskManager.createTask('Tag Test');

    expect(taskManager.addTagToTask(taskId, 'test-tag')).toBe(true);
    expect(taskManager.getTaskDetails(taskId).tags).toContain('test-tag');

    expect(taskManager.removeTagFromTask(taskId, 'test-tag')).toBe(true);
    expect(taskManager.getTaskDetails(taskId).tags).not.toContain('test-tag');
  });

  test('should delete a task', () => {
    const taskId = taskManager.createTask('Delete Test');

    expect(taskManager.getTaskDetails(taskId)).toBeDefined();
    expect(taskManager.deleteTask(taskId)).toBe(true);
    expect(taskManager.getTaskDetails(taskId)).toBeUndefined();
  });

  test('should list tasks with filters', () => {
    const todoId = taskManager.createTask('Todo Task', '', TaskPriority.LOW);
    const ipId = taskManager.createTask('In Progress Task', '', TaskPriority.MEDIUM);

    taskManager.updateTaskStatus(ipId, TaskStatus.IN_PROGRESS);

    expect(taskManager.listTasks().length).toBe(2);
    expect(taskManager.listTasks(TaskStatus.TODO).length).toBe(1);
    expect(taskManager.listTasks(null, TaskPriority.MEDIUM).length).toBe(1);
  });

  test('should get statistics', () => {
    taskManager.createTask('Task 1', '', TaskPriority.LOW);
    const id2 = taskManager.createTask('Task 2', '', TaskPriority.MEDIUM);
    taskManager.updateTaskStatus(id2, TaskStatus.IN_PROGRESS);
    const id3 = taskManager.createTask('Task 3', '', TaskPriority.HIGH);
    taskManager.updateTaskStatus(id3, TaskStatus.DONE);

    const stats = taskManager.getStatistics();

    expect(stats.total).toBe(3);
    expect(stats.byStatus[TaskStatus.TODO]).toBe(1);
    expect(stats.byStatus[TaskStatus.IN_PROGRESS]).toBe(1);
    expect(stats.byStatus[TaskStatus.DONE]).toBe(1);
  });
});
