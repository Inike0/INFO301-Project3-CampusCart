"""Run from the project folder: python -m unittest discover -s tests -v"""

import csv
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import ShopError, ShopStore, parse_money, parse_whole_number


class CampusCartTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.shop = ShopStore(Path(self.folder.name) / "data")
        self.customer = self.shop.register_customer("Demo Customer", "000-000", "demo@example.com")
        self.product = self.shop.add_product("Study Notebook", "2.25", 10)

    def test_creates_all_csv_files_with_headers(self):
        for name in ("products", "customers", "orders", "order_items"):
            path = Path(self.folder.name) / "data" / f"{name}.csv"
            self.assertTrue(path.exists())
            with path.open(newline="", encoding="utf-8") as stream:
                self.assertTrue(next(csv.reader(stream)))

    def test_product_add_and_list(self):
        self.assertEqual(self.shop.find_product(self.product)["name"], "Study Notebook")

    def test_product_search_by_id_and_name(self):
        self.assertEqual(len(self.shop.search_products(self.product.lower())), 1)
        self.assertEqual(len(self.shop.search_products("noteBOOK")), 1)
        self.assertEqual(self.shop.search_products("not present"), [])

    def test_empty_product_name_rejected(self):
        with self.assertRaises(ShopError):
            self.shop.add_product("   ", "1.00", 2)

    def test_negative_price_rejected(self):
        with self.assertRaises(ShopError):
            self.shop.add_product("Bad price", "-1", 3)

    def test_more_than_two_decimal_places_rejected(self):
        with self.assertRaises(ShopError):
            self.shop.add_product("Bad precision", "1.234", 3)

    def test_non_numeric_price_and_nan_rejected(self):
        for raw in ("hello", "NaN", "Infinity", ""):
            with self.subTest(raw=raw), self.assertRaises(ShopError):
                parse_money(raw)

    def test_zero_price_permitted(self):
        product_id = self.shop.add_product("Sample Giveaway", "0", 1)
        self.assertEqual(self.shop.find_product(product_id)["price"], "0.00")

    def test_negative_or_fractional_stock_rejected(self):
        for invalid in ("-1", "2.5", "two", ""):
            with self.subTest(invalid=invalid), self.assertRaises(ShopError):
                self.shop.add_product("Bad stock", "2.00", invalid)

    def test_update_product(self):
        self.shop.update_product(self.product, name="Updated Notebook", price="3.75", stock=6)
        p = self.shop.find_product(self.product)
        self.assertEqual((p["name"], p["price"], p["stock"]), ("Updated Notebook", "3.75", "6"))

    def test_remove_product_and_new_unique_id(self):
        self.shop.remove_product(self.product)
        self.assertIsNone(self.shop.find_product(self.product))
        next_id = self.shop.add_product("New item", "10", 1)
        # Product IDs are unique among active products and past order items.
        self.assertEqual(len({p["product_id"] for p in self.shop.list_products()}), 1)
        self.assertNotEqual(next_id, "")

    def test_customer_registration_search_and_update(self):
        self.assertTrue(self.shop.find_customer(self.customer))
        self.assertEqual(len(self.shop.search_customers("demo")), 1)
        self.shop.update_customer(self.customer, name="New Name", email="new@example.com")
        self.assertEqual(self.shop.find_customer(self.customer)["name"], "New Name")

    def test_reject_invalid_customer_email(self):
        with self.assertRaises(ShopError):
            self.shop.register_customer("J D", email="not-an-email")

    def test_reject_invalid_cart_quantities(self):
        for invalid in (0, -2, "abc", "2.5", ""):
            with self.subTest(invalid=invalid), self.assertRaises(ShopError):
                self.shop.cart_summary({self.product: invalid})

    def test_reject_insufficient_stock_without_reduction(self):
        with self.assertRaises(ShopError):
            self.shop.place_order(self.customer, {self.product: 11})
        self.assertEqual(self.shop.find_product(self.product)["stock"], "10")
        self.assertEqual(self.shop.list_orders(), [])

    def test_reject_missing_customer_and_empty_cart(self):
        with self.assertRaises(ShopError):
            self.shop.place_order("C999", {self.product: 1})
        with self.assertRaises(ShopError):
            self.shop.place_order(self.customer, {})

    def test_cart_total_calculation_uses_decimal(self):
        other = self.shop.add_product("Pen", "3.10", 9)
        items, total = self.shop.cart_summary({self.product: 2, other: 3})
        self.assertEqual(len(items), 2)
        self.assertEqual(total, Decimal("13.80"))

    def test_checkout_saves_two_csvs_and_reduces_stock(self):
        other = self.shop.add_product("Pen", "3.10", 9)
        order = self.shop.place_order(self.customer, {self.product: 2, other: 3})
        self.assertEqual(order["order_id"], "O001")
        self.assertEqual(order["total"], "13.80")
        self.assertEqual(order["item_count"], "5")
        self.assertEqual(len(self.shop.list_orders()), 1)
        self.assertEqual(len(self.shop.order_items("O001")), 2)
        self.assertEqual(self.shop.find_product(self.product)["stock"], "8")
        self.assertEqual(self.shop.find_product(other)["stock"], "6")

    def test_order_id_uniqueness_and_history_filter(self):
        order1 = self.shop.place_order(self.customer, {self.product: 1})
        order2 = self.shop.place_order(self.customer, {self.product: 2})
        self.assertNotEqual(order1["order_id"], order2["order_id"])
        self.assertEqual(len(self.shop.list_orders(customer_id=self.customer)), 2)
        self.assertEqual(len(self.shop.list_orders(order_id=order2["order_id"])), 1)
        self.assertEqual(self.shop.list_orders(order_id="O999"), [])

    def test_report_number_and_order_value(self):
        self.shop.place_order(self.customer, {self.product: 3})
        report = self.shop.report()
        self.assertEqual(report["order_count"], 1)
        self.assertEqual(report["order_value"], Decimal("6.75"))
        self.assertEqual(report["product_count"], 1)

    def test_low_stock_threshold(self):
        self.shop.update_product(self.product, stock=3)
        self.assertEqual(len(self.shop.low_stock(5)), 1)
        self.assertEqual(self.shop.low_stock(2), [])

    def test_changes_persist_after_reopening_store(self):
        order = self.shop.place_order(self.customer, {self.product: 2})
        reloaded = ShopStore(Path(self.folder.name) / "data")
        self.assertEqual(reloaded.find_product(self.product)["stock"], "8")
        self.assertEqual(len(reloaded.order_items(order["order_id"])), 1)
        self.assertTrue(reloaded.find_customer(self.customer))

    def test_historical_order_items_survive_product_deletion(self):
        order = self.shop.place_order(self.customer, {self.product: 1})
        self.shop.remove_product(self.product)
        self.assertEqual(self.shop.order_items(order["order_id"])[0]["product_name"], "Study Notebook")
        next_code = self.shop.add_product("Replacement", "2.00", 3)
        self.assertNotEqual(next_code, self.product)

    def test_customer_with_order_cannot_be_deleted(self):
        self.shop.place_order(self.customer, {self.product: 1})
        with self.assertRaises(ShopError):
            self.shop.remove_customer(self.customer)
        self.assertIsNotNone(self.shop.find_customer(self.customer))

    def test_invalid_csv_header_is_not_overwritten(self):
        path = Path(self.folder.name) / "data" / "products.csv"
        path.write_text("wrong,columns\n", encoding="utf-8")
        with self.assertRaises(ShopError):
            ShopStore(Path(self.folder.name) / "data")
        self.assertEqual(path.read_text(), "wrong,columns\n")

    def test_failed_checkout_restore_preserves_csv_records(self):
        old_save = self.shop._save_rows
        def fail_products(kind, rows):
            if kind == "products":
                raise ShopError("Simulated disk write failure")
            return old_save(kind, rows)
        with patch.object(self.shop, "_save_rows", side_effect=fail_products):
            with self.assertRaises(ShopError):
                self.shop.place_order(self.customer, {self.product: 2})
        self.assertEqual(self.shop.list_orders(), [])
        self.assertEqual(self.shop.order_items("O001"), [])
        self.assertEqual(self.shop.find_product(self.product)["stock"], "10")

    def test_order_records_exclude_payment_fields(self):
        self.shop.place_order(self.customer, {self.product: 1})
        with (Path(self.folder.name) / "data" / "orders.csv").open() as file:
            header = file.readline().lower()
        self.assertNotIn("card", header)
        self.assertNotIn("payment", header)

    def test_positive_whole_number_parser(self):
        self.assertEqual(parse_whole_number("0003", "quantity"), 3)
        for raw in (0, "-1", "3.2", "none", ""):
            with self.subTest(raw=raw), self.assertRaises(ShopError):
                parse_whole_number(raw, "quantity")


if __name__ == "__main__":
    unittest.main()
