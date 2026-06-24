# Task Manager CLI — Step-by-Step User Guide

## Getting started

### Prerequisites

- Node.js version 12 or higher
- npm (bundled with Node.js)

### Installation

```bash
# Navigate to the project directory
cd task-manager/javascript

# Install dependencies
npm install
```

---

## Step 1: Create your first task

Create a simple task with just a title:

```bash
node cli.js create "Buy groceries"
```

Output:
```
Created task with ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Add details to a task

Use options to add description, priority, due date, and tags:

```bash
node cli.js create "Write quarterly report" \
  -d "Compile Q2 metrics and analysis" \
  -p 3 \
  -u 2026-07-15 \
  -t "work,urgent"
```

Options:
- `-d` or `--description` — detailed description
- `-p` or `--priority` — priority level (1 = LOW, 2 = MEDIUM, 3 = HIGH, 4 = URGENT)
- `-u` or `--due` — due date in YYYY-MM-DD format
- `-t` or `--tags` — comma-separated list of tags

---

## Step 2: View your tasks

### List all tasks

```bash
node cli.js list
```

Output:
```
[ ] a1b2c3d4 - !! Buy groceries
  No description
  No due date | No tags
  Created: 2026-06-24 14:30:00
--------------------------------------------------
[ ] e5f6g7h8 - !!! Write quarterly report
  Compile Q2 metrics and analysis
  Due: 2026-07-15 | Tags: work, urgent
  Created: 2026-06-24 14:35:00
--------------------------------------------------
```

### Filter tasks

Filter by status:
```bash
node cli.js list -s todo
```

Filter by priority:
```bash
node cli.js list -p 3
```

Show only overdue tasks:
```bash
node cli.js list -o
```

---

## Step 3: Update task status

Tasks move through four statuses:

```
todo → in_progress → review → done
```

Mark a task as in progress:
```bash
node cli.js status <task-id> in_progress
```

Mark a task as done (automatically sets completion timestamp):
```bash
node cli.js status <task-id> done
```

---

## Step 4: Set priority

Assign or change a task's priority:

```bash
node cli.js priority <task-id> 4
```

Priority levels:
| Value | Label |
|-------|-------|
| 1 | LOW |
| 2 | MEDIUM (default) |
| 3 | HIGH |
| 4 | URGENT |

---

## Step 5: Manage due dates

Set a due date:

```bash
node cli.js due <task-id> 2026-08-01
```

Date format must be `YYYY-MM-DD`. Overdue tasks are automatically flagged when listing with the `-o` flag.

---

## Step 6: Use tags

Tags help you categorize and filter tasks.

Add a tag:
```bash
node cli.js tag <task-id> frontend
```

Remove a tag:
```bash
node cli.js untag <task-id> frontend
```

---

## Step 7: View task details

See full information about a single task:

```bash
node cli.js show <task-id>
```

Output:
```
[>] a1b2c3d4 - !!!! Deploy to production
  Deploy v2.0 to production servers
  Due: 2026-07-15 | Tags: deploy, production
  Created: 2026-06-24 15:00:00
```

---

## Step 8: Delete a task

Remove a task permanently:

```bash
node cli.js delete <task-id>
```

Output:
```
Deleted task a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Step 9: View statistics

Get an overview of your task board:

```bash
node cli.js stats
```

Output:
```
Total tasks: 12
By status:
  todo: 5
  in_progress: 3
  review: 2
  done: 2
By priority:
  1: 2
  2: 4
  3: 4
  4: 2
Overdue tasks: 1
Completed in last 7 days: 2
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `command not found: node` | Install Node.js from nodejs.org |
| Invalid date error | Use YYYY-MM-DD format, e.g., `2026-12-31` |
| Task not found | The ID may be incorrect. Run `list` to see all task IDs |
| Tag not removed | Check the tag exists with `show <id>` |
| Tasks missing after restart | Ensure `tasks.json` is in the same directory as cli.js |
