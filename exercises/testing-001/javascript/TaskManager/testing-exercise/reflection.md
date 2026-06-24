# Reflection — Testing Exercise

## How the AI's explanation compared to documentation

The AI's main advantage was **interactivity** — it asked me questions about what I thought the function did, then pointed out gaps. Documentation (a textbook or blog post) would tell me *how* to test but not *what I personally missed*. For example, when I listed edge cases for `calculateTaskScore`, the AI asked about the REVIEW status penalty (which I had forgotten), the case where a task has *both* a critical tag and is overdue (combination testing), and what happens when an invalid priority value is passed (defensive testing). Documentation would show those as a static list; the AI made me discover them by prompting.

For the TDD section, the AI was also better at keeping me in the TDD cycle — it asked "what would the first test be?" before letting me implement, then "what minimal code makes that pass?" before letting me write the logic. A tutorial would show the finished product all at once, skipping the discipline of red → green → refactor.

## What aspects would have been difficult to diagnose manually

The **time-dependent nature** of `calculateTaskScore` would have been the hardest to test manually. The function calls `new Date()` inside itself, so any test I write today might pass but give a different result tomorrow (e.g., due date tests that use relative offsets). Without `jest.useFakeTimers`, tests would be flaky and non-repeatable.

The **boundary conditions** in the due date logic were also subtle. The `if/else if` chain in the function checks:
- `daysUntilDue < 0` → overdue
- `daysUntilDue === 0` → today
- `daysUntilDue <= 2` → 1-2 days
- `daysUntilDue <= 7` → 3-7 days

These overlap — day 0 could match both the "today" and "<=2" branches if the else-if chain were ordered wrong. Manually tracing the code path for each date offset would be tedious.

## How I would modify the code to provide better error messages

Two specific improvements:

1. **Log the score breakdown** — `calculateTaskScore` returns a single number with no traceability. I would add a debug mode that logs each modifier:

   ```js
   function calculateTaskScore(task, options = {}) {
     const breakdown = []; // debug info
     let score = priorityWeights[task.priority] * 10;
     breakdown.push(`base: ${score}`);
     // ... each modifier pushes to breakdown ...
     if (options.debug) console.log('Score breakdown:', breakdown.join(' → '));
     return score;
   }
   ```

2. **Validate inputs** — if `task` is null or undefined, the caller gets a confusing `TypeError: Cannot read properties of null`. I'd add a guard:
   ```js
   if (!task || typeof task.priority === 'undefined') {
     console.error('calculateTaskScore: invalid task', task);
     return 0;
   }
   ```

## Did the AI help understand not just the fix, but the underlying concepts?

Yes — the exercise's TDD part was the most valuable for this. Writing the failing test first forced me to think about **what correct behavior looks like** before I wrote any fix code. The bug fix TDD (daysSinceUpdate) was particularly instructive: I had to decide the *expected* behavior first (date-only comparison), encode that as a test assertion, and *then* fix the code to match.

The concept that stuck most was **testing behavior, not implementation**. My first tests used relative assertions (`toBeGreaterThan`), which only check ordering, not correctness. The AI guided me toward exact-value assertions (`toBe`), which catch regressions immediately if the scoring formula changes.

## Which verification technique was most valuable

**Exact assertions with controlled time** was the single most valuable technique. Before this exercise, I would have written:

```js
expect(calculateTaskScore(overdueTask)).toBeGreaterThan(calculateTaskScore(normalTask));
```

Now I write:

```js
jest.useFakeTimers().setSystemTime(fixedDate);
expect(calculateTaskScore(overdueTask)).toBe(50);
```

The difference is that the second version:
- Catches the exact score value, not just a relationship
- Is deterministic — same result every run
- Documents the expected behavior in the assertion itself
- Fails loudly if any part of the formula changes
