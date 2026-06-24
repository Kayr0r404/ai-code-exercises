# Exercise 4: Code Documentation

## Documented Code

### models.js
```javascript
/**
 * Priority levels for tasks.
 * @enum {number}
 */
const TaskPriority = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  URGENT: 4
};

/**
 * Lifecycle statuses for tasks.
 * @enum {string}
 */
const TaskStatus = {
  TODO: 'todo',
  IN_PROGRESS: 'in_progress',
  REVIEW: 'review',
  DONE: 'done'
};

/**
 * Represents a single task with its properties and behavior.
 */
class Task {
  /**
   * @param {string} title - Task title
   * @param {string} [description=''] - Task description
   * @param {number} [priority=TaskPriority.MEDIUM] - Priority level 1-4
   * @param {Date|null} [dueDate=null] - Due date
   * @param {string[]} [tags=[]] - Categorization tags
   */
  constructor(title, description = '', priority = TaskPriority.MEDIUM, dueDate = null, tags = [])

  /**
   * Updates task properties. Only existing properties are modified.
   * @param {Object} updates - Key-value pairs of properties to update
   */
  update(updates)

  /**
   * Marks task as done, setting status, completedAt, and updatedAt.
   */
  markAsDone()

  /**
   * Checks if task is overdue (past due date and not done).
   * @returns {boolean}
   */
  isOverdue()
}
```

### app.js
```javascript
/**
 * Core business logic for task management.
 * Coordinates between CLI, storage, and model layers.
 */
class TaskManager {
  /**
   * @param {string} [storagePath='tasks.json'] - Path to storage file
   */
  constructor(storagePath = 'tasks.json')

  /**
   * Creates a new task and persists it.
   * @param {string} title
   * @param {string} [description='']
   * @param {number} [priorityValue=2] - Priority 1-4
   * @param {string|null} [dueDateStr=null] - Date in YYYY-MM-DD format
   * @param {string[]} [tags=[]]
   * @returns {string|null} - Task ID or null on invalid input
   */
  createTask(title, description, priorityValue, dueDateStr, tags)

  /**
   * Lists tasks with optional filtering.
   * @param {string|null} statusFilter - Filter by TaskStatus
   * @param {number|null} priorityFilter - Filter by TaskPriority
   * @param {boolean} [showOverdue=false] - Show only overdue
   * @returns {Task[]}
   */
  listTasks(statusFilter, priorityFilter, showOverdue)

  /**
   * Updates task status. Uses markAsDone() for DONE status.
   * @param {string} taskId
   * @param {string} newStatusValue - Valid TaskStatus value
   * @returns {boolean}
   */
  updateTaskStatus(taskId, newStatusValue)

  /**
   * Returns statistics about all tasks.
   * @returns {{total: number, byStatus: Object, byPriority: Object, overdue: number, completedLastWeek: number}}
   */
  getStatistics()
}
```

### storage.js
```javascript
/**
 * Handles persistence of tasks to a JSON file on disk.
 */
class TaskStorage {
  /**
   * @param {string} storagePath - Path to the JSON storage file
   */
  constructor(storagePath = 'tasks.json')

  /** Loads tasks from disk, restoring full Task objects. */
  load()

  /** Persists all tasks to disk as JSON array. */
  save()

  /**
   * Adds a task and persists.
   * @param {Task} task
   * @returns {string} - The task's ID
   */
  addTask(task)

  /**
   * Retrieves a task by ID.
   * @param {string} taskId
   * @returns {Task|undefined}
   */
  getTask(taskId)

  /**
   * Updates a task's properties and persists.
   * @param {string} taskId
   * @param {Object} updates
   * @returns {boolean} - Whether the update succeeded
   */
  updateTask(taskId, updates)

  /**
   * Deletes a task and persists.
   * @param {string} taskId
   * @returns {boolean} - Whether deletion succeeded
   */
  deleteTask(taskId)

  /** @returns {Task[]} - All tasks */
  getAllTasks()

  /** @param {string} status - Filter by TaskStatus */
  getTasksByStatus(status)

  /** @param {number} priority - Filter by TaskPriority */
  getTasksByPriority(priority)

  /** @returns {Task[]} - Overdue tasks */
  getOverdueTasks()
}
```
