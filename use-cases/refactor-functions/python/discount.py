VIP_DISCOUNT_RATE = 0.05
MEMBER_DISCOUNT_RATE = 0.02
MEMBER_MIN_MONTHS = 6


def calculate_cart_total(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total


def _calculate_promotion_discount(cart_total, promotions):
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


def _calculate_status_discount(cart_total, user):
    status = user.get('status', 'regular')
    months = user.get('months', 0)

    if status == 'vip':
        return cart_total * VIP_DISCOUNT_RATE
    elif status == 'member' and months > MEMBER_MIN_MONTHS:
        return cart_total * MEMBER_DISCOUNT_RATE

    return 0


def calculate_discount(cart, promotions, user):
    cart_total = calculate_cart_total(cart)
    promotion_discount, free_shipping = _calculate_promotion_discount(cart_total, promotions)
    status_discount = _calculate_status_discount(cart_total, user)
    best_discount = max(promotion_discount, status_discount)

    return {
        'original': cart_total,
        'discount': best_discount,
        'final': cart_total - best_discount,
        'free_shipping': free_shipping
    }
