import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))
from HW23.order_processor import process_orders


class TestProcessOrders(unittest.TestCase):

    def test_product_not_in_inventory(self):
        inventory = {"apple": 10, "banana": 5}
        orders = [{"product": "orange", "quantity": 2}]

        with self.assertRaises(ValueError) as context:
            process_orders(orders, inventory)
        self.assertIn("not found in inventory", str(context.exception))
    def test_insufficient_stock(self):
        inventory = {"apple": 10, "banana": 5}
        orders = [{"product": "apple", "quantity": 15}]

        with self.assertRaises(ValueError) as context:
            process_orders(orders, inventory)
        self.assertIn("Not enough stock", str(context.exception))
    def test_successful_orders_and_stock_deduction(self):
        inventory = {"apple": 10, "banana": 5}
        orders = [
            {"product": "apple", "quantity": 4},
            {"product": "banana", "quantity": 2},
        ]

        result = process_orders(orders, inventory)

        self.assertEqual(inventory["apple"], 6)
        self.assertEqual(inventory["banana"], 3)
        self.assertEqual(result, orders)


if __name__ == "__main__":
    unittest.main()