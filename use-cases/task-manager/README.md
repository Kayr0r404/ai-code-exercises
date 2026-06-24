# Task Manager CLI

A command-line task management application with multiple language implementations. Create, organize, and track tasks directly from your terminal with priorities, due dates, tags, and status tracking.

## Features

- **Create tasks** — add tasks with title, description, priority (1–4), due date, and tags
- **List tasks** — view all tasks with optional filters by status, priority, or overdue
- **Track status** — move tasks through `todo` → `in_progress` → `review` → `done`
- **Set priorities** — LOW (1), MEDIUM (2), HIGH (3), URGENT (4)
- **Manage due dates** — set and update deadlines; view overdue tasks
- **Tag system** — add and remove tags for categorization and filtering
- **Task details** — inspect full task information including timestamps
- **Statistics** — totals by status, priority, overdue count, and weekly completions
- **Persistent storage** — data saved to a local JSON file

## Implementations

| Language | Directory | Framework |
|----------|-----------|-----------|
| JavaScript | `javascript/` | Commander.js |
| Java | `java/` | Apache Commons CLI |
| Python | `python/` | argparse |

## Quick start (JavaScript)

```bash
cd javascript
npm install
node cli.js create "Write documentation" -d "Complete the README" -p 3 -u 2026-07-01 -t "docs"
node cli.js list
node cli.js stats
```

## Commands

| Command | Description |
|---------|-------------|
| `create <title>` | Create a new task |
| `list` | List all tasks (with optional filters) |
| `status <id> <status>` | Update task status |
| `priority <id> <priority>` | Update task priority |
| `due <id> <date>` | Update due date |
| `tag <id> <tag>` | Add a tag |
| `untag <id> <tag>` | Remove a tag |
| `show <id>` | Show task details |
| `delete <id>` | Delete a task |
| `stats` | Show task statistics |

## Architecture

The JavaScript implementation follows a three-layer architecture:

```
cli.js       — CLI layer (Commander.js) — command definitions and user interaction
app.js       — Business logic (TaskManager class) — coordinates operations
models.js    — Domain model (Task, TaskPriority, TaskStatus) — data structures
storage.js   — Persistence layer (TaskStorage) — JSON file read/write
```

### Data model

- **Task** — id (UUID v4), title, description, priority, status, createdAt, updatedAt, dueDate, completedAt, tags
- **Priority** — LOW (1), MEDIUM (2), HIGH (3), URGENT (4)
- **Status** — todo, in_progress, review, done

## Dependencies

- Node.js 12+ (JavaScript)
- [commander](https://github.com/tj/commander.js) — CLI argument parsing
- [uuid](https://github.com/uuidjs/uuid) — unique ID generation

## Exercises

This repository contains documentation exercises in the `javascript/` directory:

| Exercise | Topic |
|----------|-------|
| `exercise1-code-understanding.md` | Code understanding |
| `exercise2-algorithm-deconstruction.md` | Algorithm deconstruction |
| `exercise3-knowing-where-to-start.md` | Knowing where to start |
| `exercise4-code-documentation.md` | Code documentation |
| `exercise5-readme-documentation.md` | README documentation |

## Project status

Code exercise focused on CLI design, layered architecture, and multi-language implementation.
