# Task Manager CLI — Frequently Asked Questions

## Getting started

### What is Task Manager CLI?

Task Manager CLI is a command-line application that lets you create, organize, and track tasks directly from your terminal. It stores tasks in a local JSON file and provides a full set of CRUD operations with status tracking, priorities, due dates, and tags.

### How do I install it?

```bash
cd task-manager/javascript
npm install
```

No global installation is needed — run it with `node cli.js`.

### Do I need a database?

No. Tasks are stored in a `tasks.json` file in the project directory. No database setup required.

---

## Tasks

### How do I create a task?

```bash
node cli.js create "My task title"
```

Add optional details:
```bash
node cli.js create "My task" -d "Description" -p 3 -u 2026-12-31 -t "work,urgent"
```

### Can I set due dates?

Yes. Use the `-u` option when creating or the `due` command for existing tasks:
```bash
node cli.js create "Submit report" -u 2026-07-01
node cli.js due <task-id> 2026-07-15
```

Date format must always be `YYYY-MM-DD`.

### What priority levels are available?

| Level | Value | Symbol |
|-------|-------|--------|
| LOW | 1 | `!` |
| MEDIUM | 2 | `!!` |
| HIGH | 3 | `!!!` |
| URGENT | 4 | `!!!!` |

Default priority is MEDIUM (2).

### What statuses can a task have?

- `todo` — not started
- `in_progress` — actively being worked on
- `review` — awaiting review
- `done` — completed

### How do I mark a task as complete?

```bash
node cli.js status <task-id> done
```

When a task is marked done, its `completedAt` timestamp is recorded automatically.

### Can I add tags to tasks?

Yes. Tags are free-form text labels for categorization.
```bash
node cli.js tag <task-id> frontend
node cli.js untag <task-id> frontend
```

### How do I see all my tasks?

```bash
node cli.js list
```

Filter by status, priority, or overdue:
```bash
node cli.js list -s in_progress
node cli.js list -p 3
node cli.js list -o
```

### What happens when I delete a task?

The task is permanently removed from `tasks.json`. This action cannot be undone.

---

## Statistics

### How do I view task statistics?

```bash
node cli.js stats
```

Shows:
- Total task count
- Breakdown by status and priority
- Number of overdue tasks
- Tasks completed in the last 7 days

---

## Troubleshooting

### "Invalid date format" when setting a due date

Use the format `YYYY-MM-DD`. Example:
```bash
node cli.js due <task-id> 2026-12-25
```

### A task shows as "not found"

Run `node cli.js list` to see all task IDs. IDs are UUIDs — you only need enough characters to uniquely identify the task, but currently the tool requires the full ID.

### My tasks disappeared after closing the terminal

Tasks persist in `tasks.json` as long as you run the command from the same directory. Make sure you're in the `javascript/` directory when running commands.

### The command "node cli.js" is not recognized

Ensure you are in the `javascript/` directory and Node.js is installed:
```bash
node --version
```

### Can I use this tool with other programming languages?

There are also implementations in Java and Python in this repository. Check the `java/` and `python/` directories for alternative versions.

---

## Technical

### Where is my data stored?

In a file called `tasks.json` in the current working directory (where you run the CLI from).

### What format does tasks.json use?

Standard JSON. Each task stores: id, title, description, priority, status, createdAt, updatedAt, dueDate, completedAt, and tags.

### Is there any data validation?

Date inputs are validated for `YYYY-MM-DD` format. Priority values are passed directly to the application layer (1–4 recommended).

### How is the code organized?

The application follows a three-layer architecture:
- `cli.js` — user interface / command handling
- `app.js` — business logic and orchestration
- `models.js` + `storage.js` — data structures and persistence
