# Exercise 2: Function Refactoring (Python)

## Prompt template used

```
I need to refactor this Python function. It processes orders, updates inventory,
and tracks revenue in a single monolithic block. Break it down into smaller,
focused functions with clear responsibilities.

For each extracted function, explain:
- What it does
- What parameters it takes
- What it returns
- Why it was extracted

The function should remain functionally equivalent after refactoring.
```

## Original code

```python
def process_orders(orders, inventory, customer_data):
    results = []
    total_revenue = 0
    error_orders = []

    for order in orders:
        # Check if item is in inventory
        item_id = order['item_id']
        quantity = order['quantity']
        customer_id = order['customer_id']

        if item_id not in inventory:
            error_orders.append({'order_id': order['order_id'], 'error': 'Item not in inventory'})
            continue

        # Check if enough quantity available
        if inventory[item_id]['quantity'] < quantity:
            error_orders.append({'order_id': order['order_id'], 'error': 'Insufficient quantity'})
            continue

        # Check if customer exists
        if customer_id not in customer_data:
            error_orders.append({'order_id': order['order_id'], 'error': 'Customer not found'})
            continue

        # Calculate price
        price = inventory[item_id]['price'] * quantity

        # Apply discount if customer is premium
        if customer_data[customer_id]['premium']:
            price = price * 0.9

        # Update inventory
        inventory[item_id]['quantity'] -= quantity

        # Calculate shipping based on customer location
        shipping = 0
        if customer_data[customer_id]['location'] == 'domestic':
            if price < 50:
                shipping = 5.99
        else:
            shipping = 15.99

        # Add tax
        tax = price * 0.08

        # Calculate final price
        final_price = price + shipping + tax

        # Update total revenue
        total_revenue += final_price

        # Create result
        result = {
            'order_id': order['order_id'],
            'item_id': item_id,
            'quantity': quantity,
            'customer_id': customer_id,
            'price': price,
            'shipping': shipping,
            'tax': tax,
            'final_price': final_price
        }

        results.append(result)

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue
    }
```

## Issues identified by the AI

### 1. Single function does too much

The function handles: validation, pricing, discounting, inventory updates, shipping calculation, tax calculation, revenue tracking, and error collection. The AI identified 6 distinct responsibilities that should be separate functions.

### 2. Deeply nested conditional logic

The `for` loop contains 7 `if/elif/else` branches and nested conditions. Each level of nesting increases cognitive load.

### 3. Mutating input data (side effect)

`inventory[item_id]['quantity'] -= quantity` modifies the caller's inventory dictionary. This side effect is invisible at the call site and makes the function impure.

### 4. Inconsistent variable naming

`item_id`, `customer_id`, `order_id` use snake_case which is Pythonic, but the dictionary passed to the function might use different conventions.

### 5. Magic numbers

- `0.9` — what is this? A 10% discount?
- `5.99`, `15.99` — what are these based on?
- `0.08` — tax rate for which jurisdiction?

### 6. Error handling mixes business errors with data errors

"Item not in inventory" is a business validation error; `customer_id not in customer_data` is a data integrity error. They're collected together but might need different handling.

## Refactored version

```python
from typing import List, Dict, Any, Tuple

TAX_RATE = 0.08
PREMIUM_DISCOUNT = 0.10  # 10% discount
DOMESTIC_FREE_SHIPPING_THRESHOLD = 50.0
DOMESTIC_SHIPPING_COST = 5.99
INTERNATIONAL_SHIPPING_COST = 15.99


def process_orders(
    orders: List[Dict],
    inventory: Dict[str, Dict],
    customer_data: Dict[str, Dict]
) -> Dict:
    results = []
    error_orders = []
    total_revenue = 0.0

    for order in orders:
        error = validate_order(order, inventory, customer_data)
        if error:
            error_orders.append(error)
            continue

        item_id = order['item_id']
        quantity = order['quantity']
        customer_id = order['customer_id']
        customer = customer_data[customer_id]
        item = inventory[item_id]

        price = calculate_price(item['price'], quantity, customer)
        shipping = calculate_shipping(price, customer)
        tax = calculate_tax(price)
        final_price = calculate_final_price(price, shipping, tax)

        deduct_inventory(inventory, item_id, quantity)
        total_revenue += final_price

        results.append(build_order_result(
            order, item_id, quantity, customer_id,
            price, shipping, tax, final_price
        ))

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue,
    }


def validate_order(order: Dict, inventory: Dict, customer_data: Dict) -> Dict | None:
    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    if item_id not in inventory:
        return {'order_id': order['order_id'], 'error': 'Item not in inventory'}

    if inventory[item_id]['quantity'] < quantity:
        return {'order_id': order['order_id'], 'error': 'Insufficient quantity'}

    if customer_id not in customer_data:
        return {'order_id': order['order_id'], 'error': 'Customer not found'}

    return None


def calculate_price(unit_price: float, quantity: int, customer: Dict) -> float:
    subtotal = unit_price * quantity
    if customer.get('premium', False):
        return subtotal * (1 - PREMIUM_DISCOUNT)
    return subtotal


def calculate_shipping(price: float, customer: Dict) -> float:
    location = customer.get('location', 'international')

    if location == 'domestic':
        if price >= DOMESTIC_FREE_SHIPPING_THRESHOLD:
            return 0.0
        return DOMESTIC_SHIPPING_COST

    return INTERNATIONAL_SHIPPING_COST


def calculate_tax(price: float) -> float:
    return price * TAX_RATE


def calculate_final_price(price: float, shipping: float, tax: float) -> float:
    return price + shipping + tax


def deduct_inventory(inventory: Dict, item_id: str, quantity: int) -> None:
    inventory[item_id]['quantity'] -= quantity


def build_order_result(order, item_id, quantity, customer_id, price, shipping, tax, final_price):
    return {
        'order_id': order['order_id'],
        'item_id': item_id,
        'quantity': quantity,
        'customer_id': customer_id,
        'price': round(price, 2),
        'shipping': round(shipping, 2),
        'tax': round(tax, 2),
        'final_price': round(final_price, 2),
    }
```

## Comparison with my own ideas

**My approach** — I would have extracted 3-4 functions (validate, price, shipping). The AI extracted 7 smaller functions. I initially thought that was too many, but each function has exactly one job and the main processing loop reads like a narrative:

```
error = validate → price = calculate_price → tax = calculate_tax → shipping = calculate_shipping → final_price = calculate_final_price
```

Each is independently testable, and the constants at the top make the "magic numbers" explicit.

**What I would not have thought of:** Using `round()` in the result builder. The original returns floating-point values like `5.990000000000002` due to IEEE 754. The AI added rounding automatically.

**What I disagree with:** I'm not sure `deduct_inventory` should mutate the input dict. A purer approach would return a new inventory dict. But for performance with large inventories, mutation might be acceptable — the AI could have flagged this as a design tradeoff rather than a fix.

## What the AI flagged that I might have missed

- **Type hints** — Python 3 supports `List`, `Dict`, `Optional` as type annotations. The AI added them throughout, making the function signatures self-documenting
- **Named constants** — `TAX_RATE`, `PREMIUM_DISCOUNT` etc. I would have left the numbers inline
- **International shipping edge case** — the original `if/else` has a bug: `location == 'domestic'` → else branch applies `15.99` to ALL non-domestic locations. The AI preserved this but extracted the logic so the assumption is visible
- **Free shipping threshold** — the original charges $5.99 for domestic orders under $50, but charges nothing for orders over $50. The AI made this explicit with `DOMESTIC_FREE_SHIPPING_THRESHOLD` and a `>=` check
