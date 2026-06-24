from typing import Any


# --- Status discount rules: (rate, min_months) — None = no minimum ---
STATUS_DISCOUNT_RULES: dict[str, tuple[float, int | None]] = {
    'vip': (0.05, None),
    'member': (0.02, 6),
}


def calculate_cart_total(cart: list[dict[str, float | int]]) -> float:
    return sum(item['price'] * item['quantity'] for item in cart)


# --- Promo type dispatch table ---

def _handle_percent_promo(promo: dict[str, Any], cart_total: float) -> tuple[float, bool]:
    return (cart_total * promo['value'] / 100, False)


def _handle_fixed_promo(promo: dict[str, Any], cart_total: float) -> tuple[float, bool]:
    return (min(promo['value'], cart_total), False)


def _handle_shipping_promo(promo: dict[str, Any], cart_total: float) -> tuple[float, bool]:
    return (0, True)


_PROMO_DISPATCH: dict[str, callable] = {
    'percent': _handle_percent_promo,
    'fixed': _handle_fixed_promo,
    'shipping': _handle_shipping_promo,
}


def _calculate_promotion_discount(
    cart_total: float,
    promotions: list[dict[str, Any]],
) -> tuple[float, bool]:
    best_discount = 0.0
    free_shipping = False

    for promo in promotions:
        min_purchase = promo.get('min_purchase')
        if min_purchase is not None and cart_total < min_purchase:
            continue

        handler = _PROMO_DISPATCH.get(promo['type'])
        if handler is None:
            continue

        discount_value, ships_free = handler(promo, cart_total)
        best_discount = max(best_discount, discount_value)
        free_shipping = free_shipping or ships_free

    return best_discount, free_shipping


def _calculate_status_discount(cart_total: float, user: dict[str, Any]) -> float:
    status = user.get('status', 'regular')
    months = user.get('months', 0)
    rate, min_months = STATUS_DISCOUNT_RULES.get(status, (0, None))
    if min_months is not None and months <= min_months:
        return 0
    return cart_total * rate


def calculate_discount(
    cart: list[dict[str, float | int]],
    promotions: list[dict[str, Any]],
    user: dict[str, Any],
) -> dict[str, Any]:
    cart_total = calculate_cart_total(cart)
    promotion_discount, free_shipping = _calculate_promotion_discount(cart_total, promotions)
    status_discount = _calculate_status_discount(cart_total, user)
    best_discount = max(promotion_discount, status_discount)

    return {
        'original': cart_total,
        'discount': best_discount,
        'final': cart_total - best_discount,
        'free_shipping': free_shipping,
    }
