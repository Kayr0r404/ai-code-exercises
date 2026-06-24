# Language Understanding — Three-Activity Journal

---

## Activity 1: Idiomatic Code Transformation

**Function selected:** `_calculate_promotion_discount` from `discount.py`

**Original approach:** Manual loop with if/elif chain, no type hints, imperative accumulation.

**Idiomatic changes made:**
- Replaced `for`-loop cart total with `sum()` + generator expression
- Replaced if/elif chain with a **dispatch table** (dict of callables)
- Replaced hardcoded constants with a **rule map** for status discounts
- Added **type hints** to all function signatures
- Used `callable` type annotation for dispatch handlers

### 3 Key Learnings

**1. Dispatch tables are more Pythonic than if/elif chains for type dispatch**
The original had `if promo_type == 'percent': ... elif promo_type == 'fixed': ... elif promo_type == 'shipping': ...`. Replacing this with a dict mapping strings to handler functions eliminates the branching. Adding a new promo type is a one-line registration instead of adding another `elif` branch. This follows Python's "we're all consenting adults" philosophy — the dict IS the switch statement.

**2. `sum()` with a generator is declarative, not imperative**
```python
# Before (imperative — tells the computer *how* to add)
total = 0
for item in cart:
    total += item['price'] * item['quantity']

# After (declarative — tells the computer *what* to sum)
total = sum(item['price'] * item['quantity'] for item in cart)
```
The second version is shorter, faster (C-level iteration), and communicates intent directly. The generator expression is consumed lazily by `sum()`, so it never materializes a full list in memory.

**3. Type hints serve as living documentation**
Adding `cart: list[dict[str, float | int]]` to `calculate_cart_total` tells the caller exactly what shape of data to pass. Without type hints, you'd need to read the function body or write a docstring to discover that `cart` is a list of dicts with `price` and `quantity` keys. Type hints are checked by IDEs and tools like `mypy` but don't affect runtime — best of both worlds.

---

## Activity 2: Code Quality Detective

**Code reviewed:** `discount_original.py` — the original cryptic discount function.

```
def discount(cart,promos,user):
    d=0;tot=0
    for i in cart:tot+=i['price']*i['quantity']
    for p in promos:
        if p['type']=='percent' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=tot*p['value']/100;d=max(d,val)
        elif p['type']=='fixed' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=min(p['value'],tot);d=max(d,val)
        elif p['type']=='shipping' and tot>=p['min_purchase']:user['free_shipping']=True
    if user['status']=='vip':vd=tot*0.05;d=max(d,vd)
    elif user['status']=='member' and user['months']>6:vd=tot*0.02;d=max(d,vd)
    return {'original':tot,'discount':d,'final':tot-d,'free_shipping':user.get('free_shipping',False)}
```

### Code quality issues identified

| # | Issue | Severity | Improvement |
|---|-------|----------|-------------|
| 1 | **Single-letter variable names** (`d`, `tot`, `i`, `p`, `vd`, `val`) | High | Use descriptive names: `best_discount`, `cart_total`, `item`, `promo` |
| 2 | **Multiple statements per line** with `;` | High | One statement per line |
| 3 | **Side effect — mutates `user` dict** (`user['free_shipping']=True`) | High | Return free_shipping in result, never mutate inputs |
| 4 | **Magic numbers** (`0.05`, `0.02`, `6`) | Medium | Named constants: `VIP_DISCOUNT_RATE`, `MEMBER_MIN_MONTHS` |
| 5 | **Missing spaces around operators** | Medium | `a + b` not `a+b` |
| 6 | **No type hints** | Medium | Add type annotations |
| 7 | **No docstring or comments** | Low | Function docstring explaining purpose and return value |
| 8 | **Single monolithic function** (10 lines, 4 responsibilities) | High | Extract: cart total, promo discount, status discount, orchestrator |
| 9 | **Complex conditions on one line** (e.g., the promo evaluation) | High | Split into multiple lines with intermediate variables |
| 10 | **Inconsistent key access** — uses `p['min_purchase']` (can KeyError) vs `user.get('free_shipping', False)` | Medium | Use `.get()` defensively, or validate keys upfront |

### Code Quality Checklist (for future code reviews)

```
[ ] Variable names are descriptive (not single-letter, not abbreviated)
[ ] One statement per line (no semicolons)
[ ] No mutation of input parameters (pure functions where possible)
[ ] No magic numbers — every non-zero constant has a name
[ ] Consistent spacing around operators and after commas
[ ] Type hints on all function signatures
[ ] Functions are small (< 20 lines) and single-responsibility
[ ] Complex conditions are broken into named intermediate variables
[ ] Dict/sequence access uses .get() or is preceded by validation
[ ] No unreachable or dead code
[ ] No commented-out code
[ ] Function docstrings explain *why*, not *what* (the code says *what*)
```

### 3 Key Learnings

**1. Side effects are the most dangerous code smell in Python**
Mutating `user['free_shipping']` inside `discount()` means the caller's data is silently changed. If two promotions are evaluated, the order of iteration determines the final value of `free_shipping`. Worse, if the caller passes the same `user` dict to `discount()` multiple times, the second call sees the mutated state from the first. This is the kind of bug that takes hours to find and produces flaky tests. Rule: **never mutate a parameter you didn't create**.

**2. Line length ≠ complexity**
The original code fits in 10 lines, but each line does 3-4 things at once (e.g., line 5: condition check, discount calculation, max comparison, assignment — all on one line). Short functions can be harder to read than long ones if they pack too much into each line. Measure complexity by **responsibilities per function**, not lines of code.

**3. Magic numbers are technical debt with interest**
`0.05` (VIP rate), `0.02` (member rate), and `6` (member minimum months) appear without explanation. When the business changes the member rate to 3%, someone needs to trace through the code to find all the `0.02` literals and figure out which one is the member rate. A named constant like `MEMBER_DISCOUNT_RATE = 0.02` at the top of the module documents what the number means and centralizes the change.

---

## Activity 3: Understanding Python Decorators

**Feature chosen:** Python **decorators** — functions that modify other functions.

### What I built

Three practical decorators applied to the e-commerce discount functions:

### 1. Logging decorator (`@log_calls`)

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[{func.__name__}] called with {len(args)} positional, {len(kwargs)} keyword args")
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] returned {result}")
        return result
    return wrapper

@log_calls
def calculate_cart_total(cart):
    ...
```

**Why it matters:** Adds observability without cluttering the business logic. When debugging a complex discount calculation pipeline, you can instrument individual functions without editing their bodies. The `@wraps` decorator preserves the original function's `__name__` and `__doc__` — essential for introspection and debugging.

### 2. Caching decorator (`@memoize`)

```python
def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

@memoize
def calculate_status_discount(cart_total, user_type):
    # expensive lookup — cached after first call
    ...
```

**Why it matters:** If `calculate_status_discount` queried a database or API for the user's tier, caching would avoid redundant calls. The decorator pattern keeps caching logic separate from business logic, and you can add/remove caching by commenting out a single line.

### 3. Validation decorator (`@validate_inputs`)

```python
def validate_inputs(func):
    @wraps(func)
    def wrapper(cart, promotions, user):
        if not cart:
            raise ValueError("Cart must not be empty")
        if not all('price' in item and 'quantity' in item for item in cart):
            raise ValueError("Each cart item must have 'price' and 'quantity'")
        return func(cart, promotions, user)
    return wrapper

@validate_inputs
def calculate_discount(cart, promotions, user):
    ...
```

**Why it matters:** Input validation is a cross-cutting concern. Using a decorator keeps validation out of the function body so the function can focus on the core calculation logic.

### Practical example — full decorator applied to discount pipeline

```python
from functools import wraps
import time

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] took {elapsed*1000:.2f}ms")
        return result
    return wrapper

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"→ {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@timed
@log_calls
def calculate_discount(cart, promotions, user):
    ...  # same body as before
```

Stacking decorators: `calculate_discount` is now timed AND logged — the decorators compose vertically. Each one wraps the previous one, so `@timed` wraps `@log_calls`'s wrapper.

### 3 Key Learnings

**1. `@wraps` is non-negotiable**
Without `@wraps(func)`, the decorated function loses its `__name__`, `__doc__`, and `__module__`. This breaks debugging, documentation generation, and stack traces. Always use `from functools import wraps` and apply it to the inner wrapper function. This mistake is so common that it's literally called "losing the function's identity."

**2. Decorators enable separation of concerns**
The three decorators (logging, caching, validation) each address a different concern. Without decorators, these cross-cutting concerns would be mixed into every function body — repeated validation checks, scattered `print()` statements, manual cache management. Decorators let you write the core logic in the function body and layer the infrastructure around it.

**3. Decorator stacking order matters**
```python
@timed          # outer — wraps @log_calls's wrapper
@log_calls      # inner — wraps calculate_discount
def calculate_discount(...):
```
`@timed` measures the total time including `@log_calls`'s print statement. If you want to exclude logging time from timing, reverse the order. Understanding decorator stacking clarifies how Python resolves chained decorators: bottom-up application, top-down execution.

### Small project idea to practice decorators

Build a **simple retry decorator**:

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=0.5, allowed_exceptions=(ConnectionError, TimeoutError)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1.0)
def fetch_discount_from_service(promo_code):
    # Simulates flaky external API call
    ...
```

This practices: decorators with parameters, `@wraps`, exception handling, and closure variables.
