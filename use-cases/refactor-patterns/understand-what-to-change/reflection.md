# Reflection — Understanding What to Change with AI

## Which prompting strategy did I find most useful?

The **Code Readability Improvement** prompt (Exercise 1) was the most immediately useful because it applies to almost every codebase. The prompt asked for specific Java conventions, and the AI returned improvements tied to concrete standards (PascalCase, camelCase, `final`, `@Override`). Most importantly, it surfaced issues I wasn't looking for — SQL injection and plain-text passwords — that went far beyond naming conventions.

The **Code Duplication Detection** prompt (Exercise 3) was the least surprising — I could see the repeated loops myself — but the AI was valuable for suggesting the *right level* of abstraction: not too DRY (one massive generic function), not too wet (three copies of the same code), but a middle ground with focused, named helpers.

## What kinds of improvements did the AI suggest that I might not have thought of?

1. **Security issues in readability exercise** — I was focused on naming conventions and code structure. The AI spotted SQL injection (`' + username + '`) and plain-text password storage. These are not "readability" issues, but they're the kind of thing a junior dev writing code like `UserMgr` would miss entirely. The AI connected readability to *correctness* and *safety*.

2. **Empty/null edge cases in duplication exercise** — The original code assumes `userData` is a non-empty array. The AI added a guard clause. I would have written the refactored code and probably deployed it without thinking about the empty case, because the original "works" in the happy path.

3. **Magic number extraction in the Python exercise** — I knew `0.08` was a tax rate, but extracting `DOMESTIC_FREE_SHIPPING_THRESHOLD = 50.0` and `PREMIUM_DISCOUNT = 0.10` with explicit names made the code self-documenting. The names communicate *intent* — why 50, not what 50 is.

4. **`round()` in financial calculations** — The AI added `round(price, 2)` in the result builder. Floating-point accumulation errors are well known but easy to forget. The AI didn't just refactor the structure; it fixed a subtle data correctness issue.

## Were there any suggestions the AI made that I disagreed with?

**Exercise 1: Extracting a `UserValidator` class.** The AI suggested pulling validation into a separate class with static methods. For a small codebase with one manager class, this is over-engineering — it adds a file, a class, and an import for what could be 3 private methods. I'd keep validation in `UserManager` and extract only if validation logic is needed in multiple places.

**Exercise 2: Too many small functions.** The AI extracted 7 functions from the original. `calculate_tax(price)` is a one-liner that's called once. Extracting it adds a function call overhead (trivial) and a jump in the reader's mental model. I'd inline `calculate_tax` and `calculate_final_price` into `process_orders` if they're only used once, and keep only functions that encapsulate *decisions* (discounts, shipping tiers) rather than simple arithmetic.

**Exercise 3: Single-pass optimization.** The AI suggested computing `average` and `highest` in one pass over the data. That's an optimization that couples two independent calculations, reducing readability for marginal performance gain. I'd keep them separate unless profiling proved the loop was a bottleneck.

## How might I adapt these prompts for my specific codebase?

I'd create a template with three sections that I paste before each prompt:

```
Language: [Python/JS/Java]
Conventions: [link to team style guide]
Priority: [readability | safety | performance | maintainability]
Constraints: [existing patterns to preserve, e.g., "we use lodash not vanilla reduce"]
```

For example, if my team uses Python with Google style guide:
```
Language: Python
Conventions: Google Python Style Guide (line length 80, lowercase_with_underscore)
Priority: safety
Constraints: Must remain compatible with Python 3.8; no walrus operator
```

The prompt would then produce suggestions that match my team's actual codebase conventions rather than generic advice.

## What safeguards would I put in place before applying AI-suggested refactoring to production code?

1. **Test coverage first** — never refactor without tests. If the function doesn't have tests, write characterization tests (capture current behavior) before changing anything.
2. **Review every suggestion against team standards** — the AI doesn't know your team's style guide. Run the output through a linter before committing.
3. **Never accept security-focused suggestions blindly** — the AI spotted the SQL injection in Exercise 1, but I wouldn't deploy its fix without verifying the parameterized query API matches the actual `DatabaseConnection` class interface.
4. **One change at a time** — apply suggestions in separate commits, not a single massive refactor. This makes debugging trivial if a suggestion introduces a regression.
5. **Start with the smallest change** — for Exercise 3, the most impactful change is extracting the field name into a parameter. That's a small, safe refactor. The full restructuring with guards and helpers can come after.
