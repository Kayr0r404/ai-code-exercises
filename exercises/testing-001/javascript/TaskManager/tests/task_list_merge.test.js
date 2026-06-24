const { Task, TaskStatus, TaskPriority } = require('../models');
const { mergeTaskLists, resolveTaskConflict } = require('../task_list_merge');

describe('Task List Merge', () => {
  describe('mergeTaskLists', () => {
    test('should handle tasks that exist only locally', () => {
      const localTask = new Task('Local Task');
      const result = mergeTaskLists({ [localTask.id]: localTask }, {});

      expect(result.mergedTasks[localTask.id]).toEqual(localTask);
      expect(result.toCreateRemote[localTask.id]).toEqual(localTask);
    });

    test('should handle tasks that exist only remotely', () => {
      const remoteTask = new Task('Remote Task');
      const result = mergeTaskLists({}, { [remoteTask.id]: remoteTask });

      expect(result.mergedTasks[remoteTask.id]).toEqual(remoteTask);
      expect(result.toCreateLocal[remoteTask.id]).toEqual(remoteTask);
    });

    test('should handle tasks that exist in both sources', () => {
      const taskId = 'task-123';
      const localTask = new Task('Local Version');
      localTask.id = taskId;
      localTask.updatedAt = new Date('2023-01-01');

      const remoteTask = new Task('Remote Version');
      remoteTask.id = taskId;
      remoteTask.updatedAt = new Date('2023-01-02');

      const result = mergeTaskLists({ [taskId]: localTask }, { [taskId]: remoteTask });

      expect(result.mergedTasks[taskId].title).toBe('Remote Version');
      expect(Object.keys(result.toUpdateLocal).length).toBe(1);
    });
  });

  describe('resolveTaskConflict', () => {
    test('should use remote task when it is newer', () => {
      const local = new Task('Local');
      local.updatedAt = new Date('2023-01-01');
      const remote = new Task('Remote');
      remote.updatedAt = new Date('2023-01-02');

      const [merged, updateLocal, updateRemote] = resolveTaskConflict(local, remote);

      expect(merged.title).toBe('Remote');
      expect(updateLocal).toBe(true);
      expect(updateRemote).toBe(false);
    });

    test('should use local task when it is newer', () => {
      const local = new Task('Local');
      local.updatedAt = new Date('2023-01-02');
      const remote = new Task('Remote');
      remote.updatedAt = new Date('2023-01-01');

      const [merged, updateLocal, updateRemote] = resolveTaskConflict(local, remote);

      expect(merged.title).toBe('Local');
      expect(updateLocal).toBe(false);
      expect(updateRemote).toBe(true);
    });

    test('should prioritize completed status', () => {
      const local = new Task('Local');
      local.updatedAt = new Date('2023-01-02');
      const remote = new Task('Remote');
      remote.updatedAt = new Date('2023-01-01');
      remote.status = TaskStatus.DONE;
      remote.completedAt = new Date('2023-01-01');

      const [merged] = resolveTaskConflict(local, remote);

      expect(merged.status).toBe(TaskStatus.DONE);
      expect(merged.completedAt).toEqual(remote.completedAt);
    });

    test('should merge tags from both sources', () => {
      const local = new Task('Task');
      local.tags = ['tag1', 'tag2'];
      const remote = new Task('Task');
      remote.tags = ['tag2', 'tag3'];

      const [merged] = resolveTaskConflict(local, remote);

      expect(merged.tags).toContain('tag1');
      expect(merged.tags).toContain('tag2');
      expect(merged.tags).toContain('tag3');
      expect(merged.tags.length).toBe(3);
    });
  });
});
