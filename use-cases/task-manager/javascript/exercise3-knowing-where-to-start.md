# Exercise 3: Knowing Where to Start

## Entry Points

### Primary Entry Point: `cli.js`
The CLI is the user-facing entry point. All commands are defined here:
- `node cli.js create <title>` → starts at cli.js → app.js (createTask) → storage.js (addTask)
- `node cli.js list` → starts at cli.js → app.js (listTasks) → storage.js (getAllTasks)
- `node cli.js status <id> <status>` → cli.js → app.js (updateTaskStatus) → models.js (markAsDone) or storage.js (updateTask)

## How to Find Where to Make Changes

### Adding a new command:
1. Add the command definition in `cli.js` using `program.command(...)`
2. Add the corresponding method in `app.js` (TaskManager class)
3. Add storage method in `storage.js` if new data operations are needed
4. Add model logic in `models.js` if new task states/properties are needed

### Example: Adding a CSV export feature
1. **New file:** `task_export.js` — export logic
2. **Modify:** `app.js` — add `exportTasks()` method
3. **Modify:** `cli.js` — add `export` command
4. **Reuse:** `storage.getAllTasks()` — already exists

### Example: Adding "abandoned" task status
1. **Modify:** `models.js` — add `ABANDONED` to `TaskStatus`
2. **Modify:** `app.js` — add `markAbandonedTasks()` method
3. **Modify:** `cli.js` — add cleanup command
4. **Questions to consider:** Should abandoned tasks be hidden? Should users be notified? Should HIGH priority tasks be exempt?

## Debugging Entry Points
- Command not working? Check `cli.js` first — is the command registered?
- Wrong data returned? Check `app.js` — is the logic correct?
- Data not persisting? Check `storage.js` — is `save()` being called?
- Task state wrong? Check `models.js` — are transitions correct?
