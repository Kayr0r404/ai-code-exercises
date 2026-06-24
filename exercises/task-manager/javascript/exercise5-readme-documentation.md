# Task Manager CLI

A command-line task management application built with Node.js and Commander.js. Create, organize, and track tasks directly from your terminal with support for priorities, due dates, tags, and statuses.

## Features

- **Create tasks** — add tasks with title, description, priority (1–4), due date, and tags
- **List tasks** — view all tasks with optional filters by status, priority, or overdue
- **Track status** — move tasks through todo → in_progress → review → done
- **Set priorities** — assign LOW (1), MEDIUM (2), HIGH (3), or URGENT (4)
- **Manage due dates** — set and update deadlines; view overdue tasks
- **Tag system** — add and remove tags for categorization and filtering
- **Task details** — inspect full task information including timestamps
- **Statistics** — view totals by status, priority, overdue count, and weekly completions
- **Persistent storage** — data saved to local JSON file

## Quick Start

```bash
npm install
node cli.js create "Write documentation" -d "Complete the README" -p 3 -u 2026-07-01 -t "docs,urgent"
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

### Options

**`create`**:
- `-d, --description <text>` — task description
- `-p, --priority <1-4>` — priority level (default: 2)
- `-u, --due <YYYY-MM-DD>` — due date
- `-t, --tags <tags>` — comma-separated tags

**`list`**:
- `-s, --status <status>` — filter by status
- `-p, --priority <1-4>` — filter by priority
- `-o, --overdue` — show only overdue tasks

## Usage Examples

```bash
# Create a task with full details
node cli.js create "Deploy v2.0" -d "Deploy to production" -p 4 -u 2026-07-15 -t "deploy,production"

# List all tasks
node cli.js list

# List only high priority tasks
node cli.js list -p 3

# Show overdue tasks
node cli.js list -o

# Mark a task as in progress
node cli.js status <task-id> in_progress

# Mark a task as done
node cli.js status <task-id> done

# View task details
node cli.js show <task-id>

# View statistics
node cli.js stats
```

## Architecture

```
cli.js       — CLI layer (Commander.js). Command definitions and user interaction.
app.js       — Business logic layer (TaskManager class). Coordinates operations.
models.js    — Domain model (Task, TaskPriority, TaskStatus). Data structures.
storage.js   — Persistence layer (TaskStorage). JSON file read/write.
tasks.json   — Local database (auto-generated).
```

### Data model

- **Task** — id (UUID v4), title, description, priority, status, createdAt, updatedAt, dueDate, completedAt, tags
- **Priority** — LOW (1), MEDIUM (2), HIGH (3), URGENT (4)
- **Status** — todo, in_progress, review, done

### Status flow

```
todo → in_progress → review → done
```

When a task is marked `done`, `completedAt` is automatically recorded.

## Dependencies

- Node.js 12+
- [commander](https://github.com/tj/commander.js) — CLI argument parsing
- [uuid](https://github.com/uuidjs/uuid) — unique ID generation

## Project status

This project is a code exercise focused on CLI design and layered architecture. It demonstrates CRUD operations, state management, and persistence in a terminal-based tool.
