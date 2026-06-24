import unittest
from discount import calculate_discount as discount


class TestDiscountCalculator(unittest.TestCase):
    def test_percentage_discount(self):
        cart = [
            {'price': 50, 'quantity': 2},
            {'price': 30, 'quantity': 1}
        ]

        promos = [
            {'type': 'percent', 'value': 10, 'min_purchase': 100}
        ]

        user = {'status': 'regular', 'months': 2}

        result = discount(cart, promos, user)

        # Cart total: 50*2 + 30*1 = 130
        # Discount: 10% of 130 = 13
        self.assertEqual(result['original'], 130)
        self.assertEqual(result['discount'], 13)
        self.assertEqual(result['final'], 117)
        self.assertFalse(result['free_shipping'])

    def test_fixed_discount(self):
        cart = [
            {'price': 100, 'quantity': 1}
        ]

        promos = [
            {'type': 'fixed', 'value': 20, 'min_purchase': 50}
        ]

        user = {'status': 'regular', 'months': 2}

        result = discount(cart, promos, user)

        # Cart total: 100
        # Discount: Fixed 20
        self.assertEqual(result['original'], 100)
        self.assertEqual(result['discount'], 20)
        self.assertEqual(result['final'], 80)
        self.assertFalse(result['free_shipping'])

    def test_free_shipping(self):
        cart = [
            {'price': 75, 'quantity': 2}
        ]

        promos = [
            {'type': 'shipping', 'min_purchase': 100}
        ]

        user = {'status': 'regular', 'months': 2}

        result = discount(cart, promos, user)

        # Cart total: 75*2 = 150
        # Free shipping should be applied
        self.assertEqual(result['original'], 150)
        self.assertEqual(result['discount'], 0)
        self.assertEqual(result['final'], 150)
        self.assertTrue(result['free_shipping'])

    def test_vip_discount(self):
        cart = [
            {'price': 200, 'quantity': 1}
        ]

        promos = [
            {'type': 'percent', 'value': 2, 'min_purchase': None}
        ]

        user = {'status': 'vip', 'months': 2}

        result = discount(cart, promos, user)

        # Cart total: 200
        # VIP discount: 5% of 200 = 10
        # Promo discount: 2% of 200 = 4
        # Best discount: 10
        self.assertEqual(result['original'], 200)
        self.assertEqual(result['discount'], 10)
        self.assertEqual(result['final'], 190)
        self.assertFalse(result['free_shipping'])

    def test_member_discount(self):
        cart = [
            {'price': 50, 'quantity': 3}
        ]

        promos = []

        user = {'status': 'member', 'months': 12}

        result = discount(cart, promos, user)

        # Cart total: 50*3 = 150
        # Member discount: 2% of 150 = 3
        self.assertEqual(result['original'], 150)
        self.assertEqual(result['discount'], 3)
        self.assertEqual(result['final'], 147)
        self.assertFalse(result['free_shipping'])

    def test_best_discount_selection(self):
        cart = [
            {'price': 100, 'quantity': 2}
        ]

        promos = [
            {'type': 'percent', 'value': 10, 'min_purchase': None},
            {'type': 'fixed', 'value': 15, 'min_purchase': None}
        ]

        user = {'status': 'member', 'months': 12}

        result = discount(cart, promos, user)

        # Cart total: 100*2 = 200
        # Percent discount: 10% of 200 = 20
        # Fixed discount: 15
        # Member discount: 2% of 200 = 4
        # Best discount: 20
        self.assertEqual(result['original'], 200)
        self.assertEqual(result['discount'], 20)
        self.assertEqual(result['final'], 180)
        self.assertFalse(result['free_shipping'])


if __name__ == "__main__":
    unittest.main()
