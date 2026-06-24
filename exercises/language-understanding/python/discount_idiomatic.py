"""
Idiomatic code transformation — before and after.

Original function from discount.py used as the "before" version.
"""

from typing import Any, NamedTuple

# ============================================================================
# Original version (before idiomatic improvements)
# ============================================================================

def calculate_cart_total_original(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total


def _calculate_promotion_discount_original(cart_total, promotions):
    best_discount = 0
    free_shipping = False

    for promo in promotions:
        promo_type = promo['type']
        min_purchase = promo.get('min_purchase')
        meets_minimum = min_purchase is None or cart_total >= min_purchase

        if not meets_minimum:
            continue

        if promo_type == 'percent':
            discount_value = cart_total * promo['value'] / 100
            best_discount = max(best_discount, discount_value)

        elif promo_type == 'fixed':
            discount_value = min(promo['value'], cart_total)
            best_discount = max(best_discount, discount_value)

        elif promo_type == 'shipping':
            free_shipping = True

    return best_discount, free_shipping


# ============================================================================
# Idiomatic version — improvements explained
# ============================================================================

# Improvement 1: NamedTuple for structured promo data instead of raw dicts
class Promo(NamedTuple):
    type: str
    value: float | None = None
    min_purchase: float | None = None


# Improvement 2: Dispatch table instead of if/elif chain
# Each promo type maps to a callable that computes its discount contribution
PromoHandler = tuple[float, bool]  # (discount_amount, free_shipping)

def _handle_percent_promo(promo: Promo, cart_total: float) -> PromoHandler:
    assert promo.value is not None
    return (cart_total * promo.value / 100, False)


def _handle_fixed_promo(promo: Promo, cart_total: float) -> PromoHandler:
    assert promo.value is not None
    return (min(promo.value, cart_total), False)


def _handle_shipping_promo(promo: Promo, cart_total: float) -> PromoHandler:
    return (0, True)


PROMO_DISPATCH: dict[str, callable] = {
    'percent': _handle_percent_promo,
    'fixed': _handle_fixed_promo,
    'shipping': _handle_shipping_promo,
}


# Improvement 3: Type hints everywhere, sum() with generator
def calculate_cart_total(cart: list[dict[str, float | int]]) -> float:
    return sum(item['price'] * item['quantity'] for item in cart)


# Improvement 4: Unpacking + dict dispatch replaces if/elif
def _calculate_promotion_discount(
    cart_total: float,
    promotions: list[dict[str, Any]],
) -> tuple[float, bool]:
    best_discount = 0.0
    free_shipping = False

    for promo_dict in promotions:
        promo = Promo(**{k: v for k, v in promo_dict.items() if v is not None})

        min_purchase = promo.min_purchase
        if min_purchase is not None and cart_total < min_purchase:
            continue

        handler = PROMO_DISPATCH.get(promo.type)
        if handler is None:
            continue

        discount_value, ships_free = handler(promo, cart_total)
        best_discount = max(best_discount, discount_value)
        free_shipping = free_shipping or ships_free

    return best_discount, free_shipping


# Improvement 5: Status discount with mapping instead of if/elif
# Demonstrates functional composition pattern
STATUS_DISCOUNTS: dict[str, tuple[float, int | None]] = {
    'vip': (0.05, None),
    'member': (0.02, 6),
}

def _calculate_status_discount(cart_total: float, user: dict[str, Any]) -> float:
    status = user.get('status', 'regular')
    months = user.get('months', 0)
    rate, min_months = STATUS_DISCOUNTS.get(status, (0, None))
    if min_months is not None and months <= min_months:
        return 0
    return cart_total * rate


def calculate_discount(
    cart: list[dict[str, float | int]],
    promotions: list[dict[str, Any]],
    user: dict[str, Any],
) -> dict[str, Any]:
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
