# Error Diagnosis: Global Variable Being Overwritten (JavaScript)

## Chosen scenario — Scenario 6

---

## Error Analysis: TypeError — Variable Shadowing

### Error Description

```
Uncaught TypeError: Cannot read properties of undefined (reading 'map')
    at displayTasks (taskManager.js:24)
    at addTask (taskManager.js:15)
    at HTMLButtonElement.onclick (index.html:1)
```

`tasks.map` fails because inside `addTask`, the `let tasks = { ... }` declaration **shadows** the outer `tasks` array within the function's scope. When `displayTasks()` later tries `tasks.map(...)`, the global `tasks` was never updated — the new task object was only stored in the local variable, which evaporated when `addTask` returned. The specific "undefined" error suggests the global `tasks` was either never initialized (if `initApp` hasn't run yet) or got overwritten in an earlier interaction.

### Root Cause

Line 10 in `addTask` uses `let` instead of assigning directly to the existing `tasks`:

```js
function addTask(taskName) {
  let tasks = { id: Date.now(), name: taskName, completed: false }; // BUG: 'let' creates a NEW local variable
  displayTasks();
}
```

The `let` keyword declares a new local variable with the same name as the global `tasks`. Inside `addTask`, every reference to `tasks` now points to the local object `{ id: ..., name: ..., completed: false }` — not the global array. The new task is never pushed to the global array, so when `displayTasks` runs (where there is no local shadowing), it sees the unmodified global.

This also breaks `toggleTaskStatus` and `deleteTask` if they run after `addTask` — they expect the global `tasks` to be an array of objects, but the global was never updated.

### Solution

Remove `let` in `addTask` so the assignment targets the global variable:

```js
function addTask(taskName) {
  tasks.push({ id: Date.now(), name: taskName, completed: false });
  displayTasks();
}
```

Alternatively, use the global directly via `window.tasks`:

```js
function addTask(taskName) {
  window.tasks.push({ id: Date.now(), name: taskName, completed: false });
  displayTasks();
}
```

### Learning Points

1. **`let` shadows outer scope** — declaring `let` with an existing name inside a function creates a **new** local binding. The outer variable is completely hidden. This is the same for `const` and `var` (though `var` behaves differently with function scoping vs block scoping).

2. **Read the variable, not just the error** — the error says `.map` failed on `undefined`, but the real problem is variable shadowing two functions up the call stack. The error location (`displayTasks`) is not where the bug was introduced (`addTask`).

3. **Avoid mutable globals** — the root problem is a shared mutable global `tasks`. Multiple functions read and write it, and any accidental redeclaration corrupts the shared state. Better patterns:
   - Encapsulate state in a module or class (no free-floating globals)
   - Pass state explicitly as parameters instead of relying on shared scope
   - Use `const` for any variable you never reassign — `const` would have caught this at the `let tasks = { ... }` line because you can't redeclare a `const` in the same scope

4. **Consistent naming convention** — if locals and globals have visually distinct names (e.g., `gTasks` for global, or a module pattern), shadowing is harder to accidentally introduce.

### How the AI's explanation compared to documentation

Searching MDN for "TypeError: map is not a function" returns explanations about arrays vs objects, but wouldn't point to the **cause** — the shadowing in `addTask`. The AI traced the call stack forward from `addTask` to `displayTasks` and identified the real culprit (the `let` declaration) that `displayTasks` line 24's error would never reveal on its own. The value of the AI here is connecting the symptom (`.map` failure) to the root cause (shadowing two scopes away).

### What would have been difficult to diagnose manually

The `let` looks innocuous — a developer adding a simple feature might type `let tasks =` out of habit without realizing `tasks` already exists in an outer scope. The error message blames `displayTasks`, which is perfectly correct code. A manual debugger would need to:
- Set a breakpoint in `displayTasks` and inspect `tasks` — see it's a single object
- Then figure out how it became an object instead of an array
- Track backward through `addTask` to find the `let`

The temporal gap between the assignment (in `addTask`) and the error (in `displayTasks`) makes this non-trivial to trace by hand.

### How to provide better error messages in the future

- **Use a module pattern** — `let tasks = []` at module scope inside an IIFE or ES module is not truly global; accidental `let` inside a function shadows only that function, not the module. This limits the blast radius.
- **Adopt `use strict`** — in strict mode, assigning to an undeclared variable throws a `ReferenceError`, which would immediately reveal the mistake. Without strict mode, the shadowing silently succeeds.
- **Validate types at function boundaries** — `displayTasks` could guard: `if (!Array.isArray(tasks)) throw new Error('tasks must be an array')`. This would produce a clearer error at the exact point of failure.
- **Use TypeScript** — declaring a parameter or local with the same name as a module-level variable would likely be caught during review, and the type mismatch (`Task[]` vs `Task`) would be a compile error.

### Did the AI help understand not just the fix, but the underlying concepts?

Yes — specifically the distinction between **reassignment** and **shadowing**. The fix (`s/let tasks/tasks.push/`) is trivial, but the concept of lexical scoping — that `let` creates a new binding in the innermost enclosing block — is the real lesson. Understanding *why* `let` behaves differently from a plain assignment explains not just this bug but similar issues with loops, closures, and callback scopes.
