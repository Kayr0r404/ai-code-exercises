# Exercise 1: Code Explore Challenge - Code Understanding

## Project Structure

The Task Manager CLI application follows a 3-layer architecture:

```
cli.js (Presentation/CLI Layer)
  → app.js (Business Logic Layer)
    → storage.js (Data/Persistence Layer)
      → models.js (Domain Model)
```

### Entry Point
- `cli.js` — defined as `"main"` in `package.json`. Uses Commander.js to parse CLI commands.

### Components

| File | Purpose |
|------|---------|
| `cli.js` | CLI interface — defines commands (create, list, status, priority, stats, etc.) |
| `app.js` | TaskManager class — business logic for task operations |
| `models.js` | Task, TaskPriority, TaskStatus — domain entities |
| `storage.js` | TaskStorage — reads/writes tasks to `tasks.json` |
| `task_priority.js` | Scoring and sorting algorithms for task importance |
| `task_parser.js` | Natural language parser for creating tasks from text |
| `task_list_merge.js` | Merge logic for synchronizing local and remote task lists |

### Technology Stack
- **Runtime:** Node.js
- **Module System:** CommonJS (`require`/`module.exports`)
- **CLI Framework:** Commander.js
- **ID Generation:** uuid (v4)
- **Testing:** Jest
- **Data Storage:** JSON file on disk

## Data Flow
1. User types a command in the terminal
2. `cli.js` parses the command and arguments
3. `app.js` (TaskManager) processes the business logic
4. `storage.js` persists data to a JSON file
5. Result is returned to the user

## Architecture Decisions
- The absence of a web framework (Express, etc.) is intentional — this is a CLI tool, not an HTTP server.
- CommonJS modules allow clean separation of concerns without a build step.
- File-based JSON storage is appropriate for a local CLI tool without a backend.
