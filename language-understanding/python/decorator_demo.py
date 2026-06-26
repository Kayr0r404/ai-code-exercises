"""
Activity 3 — Python decorators on the discount calculator pipeline.

Demonstrates: @log_calls, @timed, @validate_inputs, and decorator stacking.
"""

from functools import wraps
import time


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  → {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [{func.__name__}] {elapsed*1000:.2f}ms")
        return result
    return wrapper


def validate_inputs(func):
    @wraps(func)
    def wrapper(cart, promotions, user):
        if not cart:
            raise ValueError("Cart must not be empty")
        if not all('price' in item and 'quantity' in item for item in cart):
            raise ValueError("Each cart item needs 'price' and 'quantity'")
        if not isinstance(promotions, list):
            raise ValueError("Promotions must be a list")
        return func(cart, promotions, user)
    return wrapper


# ---------------------------------------------------------------------------
# Stacking: @timed wraps @log_calls's wrapper
# ---------------------------------------------------------------------------

@timed
@log_calls
def calculate_cart_total(cart):
    return sum(item['price'] * item['quantity'] for item in cart)


@log_calls
def _calculate_promotion_discount(cart_total, promotions):
    best_discount = 0.0
    free_shipping = False

    for promo in promotions:
        min_purchase = promo.get('min_purchase')
        if min_purchase is not None and cart_total < min_purchase:
            continue

        promo_type = promo['type']
        if promo_type == 'percent':
            discount_value = cart_total * promo['value'] / 100
            best_discount = max(best_discount, discount_value)
        elif promo_type == 'fixed':
            discount_value = min(promo['value'], cart_total)
            best_discount = max(best_discount, discount_value)
        elif promo_type == 'shipping':
            free_shipping = True

    return best_discount, free_shipping


@log_calls
def _calculate_status_discount(cart_total, user):
    status_discounts = {
        'vip': (0.05, None),
        'member': (0.02, 6),
    }
    status = user.get('status', 'regular')
    months = user.get('months', 0)
    rate, min_months = status_discounts.get(status, (0, None))
    if min_months is not None and months <= min_months:
        return 0
    return cart_total * rate


@validate_inputs
@timed
@log_calls
def calculate_discount(cart, promotions, user):
    cart_total = calculate_cart_total(cart)
    promo_discount, free_shipping = _calculate_promotion_discount(cart_total, promotions)
    status_discount = _calculate_status_discount(cart_total, user)
    best_discount = max(promo_discount, status_discount)

    return {
        'original': cart_total,
        'discount': best_discount,
        'final': cart_total - best_discount,
        'free_shipping': free_shipping,
    }


# ---------------------------------------------------------------------------
# Retry decorator (advanced — parameterized, exception-aware)
# ---------------------------------------------------------------------------

def retry(max_attempts=3, delay=0.5, allowed_exceptions=(ConnectionError, TimeoutError)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    print(f"  [retry] attempt {attempt}/{max_attempts} failed: {e}")
                    last = e
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)
            raise last
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cart = [
        {'price': 100, 'quantity': 2},
        {'price': 50, 'quantity': 1},
    ]
    promos = [
        {'type': 'percent', 'value': 10, 'min_purchase': 100},
        {'type': 'fixed', 'value': 15, 'min_purchase': None},
    ]
    user = {'status': 'vip', 'months': 12}

    print("=== Decorated discount pipeline ===")
    result = calculate_discount(cart, promos, user)
    print(f"Result: {result}")

    print("\n=== Identity check ===")
    print(f"Function name preserved: {calculate_discount.__name__}")
    print(f"Docstring preserved: '{calculate_discount.__doc__}'")

    print("\n=== Retry decorator demo ===")
    state = {'call_count': 0}

    @retry(max_attempts=3, delay=0.1)
    def flaky_api_call():
        state['call_count'] += 1
        if state['call_count'] < 3:
            raise ConnectionError("Network timeout")
        return "success"

    result = flaky_api_call()
    print(f"API returned: {result} (took {state['call_count']} attempts)")
