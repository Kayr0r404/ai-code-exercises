# Code Readability Analysis — Discount Calculator

## Original code (discount_original.py)

```python
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

### Readability issues identified

| Issue | Original | Improved |
|-------|----------|----------|
| 1. Cryptic variable names | `d`, `tot`, `i`, `p`, `vd`, `val` | `best_discount`, `cart_total`, `item`, `promo`, `status_discount`, `discount_value` |
| 2. Multiple statements per line | `d=0;tot=0` | One statement per line |
| 3. No spacing around operators | `tot+=i['price']*i['quantity']` | `total += item['price'] * item['quantity']` |
| 4. No spacing after commas | `discount(cart,promos,user)` | `calculate_discount(cart, promotions, user)` |
| 5. No function docstring | — | Added docstring |
| 6. Magic numbers | `0.05`, `0.02`, `6` | Named constants `VIP_DISCOUNT_RATE`, `MEMBER_DISCOUNT_RATE`, `MEMBER_MIN_MONTHS` |
| 7. Side effect (mutates user) | `user['free_shipping'] = True` | Returns `free_shipping` in result dict |
| 8. Single monolithic function | 9 lines, all logic combined | 4 functions, single responsibility each |
| 9. Complex conditions on one line | `if p['type']=='percent' and (p['min_purchase'] is None or tot>=p['min_purchase']):val=tot*p['value']/100;d=max(d,val)` | Split across multiple lines with intermediate variables (`meets_minimum`) |

## Refactored code (discount.py)

**4 functions, each with a single responsibility:**

### 1. `calculate_cart_total(cart)` — 4 lines
Pure data transformation: item prices × quantities → total.

### 2. `_calculate_promotion_discount(cart_total, promotions)` — 18 lines
Handles all three promo types (percent, fixed, shipping). Returns a tuple `(best_discount, free_shipping)` so the `free_shipping` side effect is eliminated.

Key readability techniques:
- Early `continue` for promos that don't meet minimum purchase (reduces nesting)
- Named intermediate variable `meets_minimum` instead of inline condition
- `max()` to select best discount (clearer intent than manual comparison)

### 3. `_calculate_status_discount(cart_total, user)` — 7 lines
Encapsulates the VIP/member tier logic. Magic numbers pulled to module-level constants.

### 4. `calculate_discount(cart, promotions, user)` — 6 lines
Orchestrator: calls the three helpers, picks the best overall discount, returns the result dict.

## Reflection

### How much easier is the code to understand now?
The first time I read the original, I had to mentally execute it to figure out what `d` was accumulating. With named helpers, the pipeline is self-documenting: "calculate the cart total, find the best promotion discount, check user status, return the result." The orchestrator tells you the story in 6 lines.

### What readability issues did the AI (analysis) catch that I might have missed?
The **side-effect mutation** of `user['free_shipping']` is the most subtle issue. In a real codebase, this could cause hard-to-find bugs if the caller reuses that user object. The original returns `user.get('free_shipping', False)` — it writes to the dict and reads back from it, coupling the promo processing to the return value through a mutation.

### What readability issues might the AI miss that I noticed?
The **`min_purchase` key comparison** logic: the original uses `p['min_purchase']` but the test data has `'min_purchase'` on shipping promos too. The code accesses this key directly (`p['min_purchase']`) which will `KeyError` if a promo lacks it. My refactored version uses `.get('min_purchase')` with a default `None`, which is more defensive. This wasn't caught by tests because all test promos include `min_purchase`.

### Which readability improvements had the biggest impact?

1. **Function decomposition** — splitting into `calculate_cart_total`, `_calculate_promotion_discount`, and `_calculate_status_discount` had the single biggest impact. Each helper has exactly one job, so you don't need to hold the whole discount algorithm in your head at once.

2. **Eliminating side effects** — removing the `user['free_shipping']` mutation means the function is now a pure transformation: inputs in, result out. This makes it testable, composable, and safe to call.

3. **Named constants** — `VIP_DISCOUNT_RATE = 0.05` tells you *what* the number means, whereas `0.05` in the original code could have been anything.

### How did the improved names change understanding of the code's purpose?

The function name `discount(cart, promos, user)` is ambiguous — does it apply a discount? Calculate the best one? Return the final price? The new name `calculate_discount` makes it clear this is a calculation, not a mutation. The variable names tell you *what kind* of value they hold (`best_discount`, `cart_total`, `promotion_discount`) rather than just labeling their type (`d`, `tot`, `p`).

### Readability patterns to apply to future code

1. **One statement per line** — no semicolons. Ever.
2. **Operator spacing** — `a + b` not `a+b`. It looks trivial, but dense arithmetic without spaces is genuinely harder to scan.
3. **Early exit / continue** — filter out invalid conditions early instead of nesting deeper.
4. **Named intermediate variables** — `meets_minimum = min_purchase is None or cart_total >= min_purchase` replaces a 4-line condition with a one-word name.
5. **Pure functions** — no mutations of input parameters. Return everything the caller needs.
6. **Constants for magic numbers** — if a number isn't 0, 1, or derived from inputs, give it a name.
