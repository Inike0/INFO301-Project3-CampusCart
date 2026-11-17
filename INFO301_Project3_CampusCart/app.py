"""CampusCart: beginner-friendly CSV e-commerce console application (INFO 301).

No GUI, SQL database, network API or real-payment functionality is used.
Run: python app.py
"""

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import re
import tempfile


HEADERS = {
    "products": ["product_id", "name", "price", "stock"],
    "customers": ["customer_id", "name", "phone", "email"],
    "orders": ["order_id", "customer_id", "customer_name", "created_at", "total", "item_count"],
    "order_items": ["order_id", "product_id", "product_name", "unit_price", "quantity", "line_total"],
}


class ShopError(ValueError):
    """A safe, user-friendly message for invalid shop operations."""


def parse_money(value):
    """Accept a nonnegative amount with at most two decimal places."""
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ShopError("Price must be a valid number, for example 12.50.") from None
    if not amount.is_finite() or amount < 0:
        raise ShopError("Price must be zero or greater.")
    try:
        rounded = amount.quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ShopError("Price is too large to store safely.") from None
    if amount != rounded:
        raise ShopError("Price cannot have more than two decimal places.")
    return rounded


def parse_whole_number(value, label, allow_zero=False):
    """Reject decimals, negatives, missing values and text."""
    raw = str(value).strip()
    if not re.fullmatch(r"[0-9]+", raw):
        raise ShopError(f"{label} must be a whole number.")
    try:
        number = int(raw)
    except ValueError:
        raise ShopError(f"{label} is too large.") from None
    if number < 0 or (number == 0 and not allow_zero):
        rule = "zero or greater" if allow_zero else "greater than zero"
        raise ShopError(f"{label} must be {rule}.")
    return number


def currency(amount):
    return f"${Decimal(str(amount)):,.2f}"


def fresh_id(prefix, rows, key, historical=()):
    """Return the next ID, checking existing and historically used IDs."""
    used = [str(row[key]) for row in rows] + list(historical)
    sequence = [int(text[len(prefix):]) for text in used
                if text.startswith(prefix) and text[len(prefix):].isdigit()]
    return f"{prefix}{max(sequence, default=0) + 1:03d}"


class ShopStore:
    """All application operations and CSV persistence live in one simple class."""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for kind, headers in HEADERS.items():
            file_path = self._path(kind)
            if not file_path.exists():
                self._save_rows(kind, [])
            else:
                with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
                    existing = next(csv.reader(handle), [])
                if existing != headers:
                    raise ShopError(f"The header in {file_path.name} is invalid. Expected: {', '.join(headers)}")

    def _path(self, kind):
        return self.data_dir / (kind + ".csv")

    def _read_rows(self, kind):
        with self._path(kind).open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _save_rows(self, kind, rows):
        """Write a temporary CSV, then replace the old file to avoid half-written files."""
        target = self._path(kind)
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="",
                                             dir=self.data_dir, prefix=".pending_",
                                             suffix=".csv", delete=False) as handle:
                tmp_name = handle.name
                writer = csv.DictWriter(handle, fieldnames=HEADERS[kind], extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            os.replace(tmp_name, target)
        except OSError as exc:
            raise ShopError(f"Unable to save {target.name}: {exc}") from exc
        finally:
            if tmp_name and os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def list_products(self):
        return self._read_rows("products")

    def search_products(self, query):
        needle = str(query).strip().lower()
        return [p for p in self.list_products()
                if needle in p["product_id"].lower() or needle in p["name"].lower()]

    def find_product(self, product_id):
        code = str(product_id).strip().upper()
        return next((p for p in self.list_products() if p["product_id"] == code), None)

    def add_product(self, name, price, stock):
        name = str(name).strip()
        if not name:
            raise ShopError("Product name cannot be empty.")
        amount = parse_money(price)
        count = parse_whole_number(stock, "Stock", allow_zero=True)
        products = self.list_products()
        historic_ids = (r["product_id"] for r in self._read_rows("order_items"))
        product_id = fresh_id("P", products, "product_id", historic_ids)
        products.append({"product_id": product_id, "name": name,
                         "price": f"{amount:.2f}", "stock": str(count)})
        self._save_rows("products", products)
        return product_id

    def update_product(self, product_id, name=None, price=None, stock=None):
        products = self.list_products()
        product_id = str(product_id).strip().upper()
        target = next((p for p in products if p["product_id"] == product_id), None)
        if target is None:
            raise ShopError("Product ID not found.")
        if name is not None:
            cleaned = str(name).strip()
            if not cleaned:
                raise ShopError("Product name cannot be empty.")
            target["name"] = cleaned
        if price is not None:
            target["price"] = f"{parse_money(price):.2f}"
        if stock is not None:
            target["stock"] = str(parse_whole_number(stock, "Stock", allow_zero=True))
        self._save_rows("products", products)

    def remove_product(self, product_id):
        products = self.list_products()
        kept = [p for p in products if p["product_id"] != str(product_id).strip().upper()]
        if len(kept) == len(products):
            raise ShopError("Product ID not found.")
        # Past order_items preserve product names and prices as historical snapshots.
        self._save_rows("products", kept)

    def list_customers(self):
        return self._read_rows("customers")

    def find_customer(self, customer_id):
        code = str(customer_id).strip().upper()
        return next((c for c in self.list_customers() if c["customer_id"] == code), None)

    def search_customers(self, query):
        needle = str(query).strip().lower()
        return [c for c in self.list_customers()
                if needle in c["customer_id"].lower() or needle in c["name"].lower()]

    def register_customer(self, name, phone="", email=""):
        name = str(name).strip()
        if not name:
            raise ShopError("Customer name cannot be empty.")
        phone, email = str(phone).strip(), str(email).strip()
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ShopError("Email must resemble name@example.com, or be left empty.")
        customers = self.list_customers()
        historic_ids = (r["customer_id"] for r in self._read_rows("orders"))
        customer_id = fresh_id("C", customers, "customer_id", historic_ids)
        customers.append({"customer_id": customer_id, "name": name,
                          "phone": phone, "email": email})
        self._save_rows("customers", customers)
        return customer_id

    def update_customer(self, customer_id, name=None, phone=None, email=None):
        customers = self.list_customers()
        code = str(customer_id).strip().upper()
        customer = next((c for c in customers if c["customer_id"] == code), None)
        if customer is None:
            raise ShopError("Customer ID not found.")
        if name is not None:
            if not str(name).strip():
                raise ShopError("Customer name cannot be empty.")
            customer["name"] = str(name).strip()
        if phone is not None:
            customer["phone"] = str(phone).strip()
        if email is not None:
            cleaned = str(email).strip()
            if cleaned and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", cleaned):
                raise ShopError("Invalid email format.")
            customer["email"] = cleaned
        self._save_rows("customers", customers)

    def remove_customer(self, customer_id):
        code = str(customer_id).strip().upper()
        if any(r["customer_id"] == code for r in self._read_rows("orders")):
            raise ShopError("Cannot delete a customer with past orders. Edit the record instead.")
        customers = self.list_customers()
        kept = [c for c in customers if c["customer_id"] != code]
        if len(kept) == len(customers):
            raise ShopError("Customer ID not found.")
        self._save_rows("customers", kept)

    def cart_summary(self, cart):
        """Validate every cart line and return item snapshots and its exact total."""
        products = {p["product_id"]: p for p in self.list_products()}
        items = []
        total = Decimal("0.00")
        for product_id, raw_quantity in cart.items():
            product_id = str(product_id).strip().upper()
            quantity = parse_whole_number(raw_quantity, "Order quantity")
            product = products.get(product_id)
            if product is None:
                raise ShopError(f"Product {product_id} is no longer available.")
            if quantity > int(product["stock"]):
                raise ShopError(f"Not enough stock for {product_id}. Available: {product['stock']}.")
            price = parse_money(product["price"])
            line_total = price * quantity
            items.append({"product_id": product_id, "product_name": product["name"],
                          "unit_price": f"{price:.2f}", "quantity": str(quantity),
                          "line_total": f"{line_total:.2f}"})
            total += line_total
        return items, total

    def place_order(self, customer_id, cart):
        """Confirm a simulated order; save header, lines and reduced stock to CSV."""
        customer = self.find_customer(customer_id)
        if customer is None:
            raise ShopError("Customer ID not found. Please register a customer first.")
        if not cart:
            raise ShopError("Your shopping cart is empty.")
        lines, total = self.cart_summary(cart)  # Validate all lines before changing anything.
        current_orders = self._read_rows("orders")
        current_items = self._read_rows("order_items")
        current_products = self.list_products()
        order_id = fresh_id("O", current_orders, "order_id")
        order = {"order_id": order_id, "customer_id": customer["customer_id"],
                 "customer_name": customer["name"],
                 "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                 "total": f"{total:.2f}", "item_count": str(sum(int(x["quantity"]) for x in lines))}
        new_orders = current_orders + [order]
        new_items = current_items + [{"order_id": order_id, **line} for line in lines]
        quantities = {line["product_id"]: int(line["quantity"]) for line in lines}
        new_products = [dict(p) for p in current_products]
        for product in new_products:
            if product["product_id"] in quantities:
                product["stock"] = str(int(product["stock"]) - quantities[product["product_id"]])
        # CSV has no multi-file transactions. Retain copies for best-effort rollback.
        snapshots = {kind: self._path(kind).read_bytes()
                     for kind in ("orders", "order_items", "products")}
        try:
            self._save_rows("orders", new_orders)
            self._save_rows("order_items", new_items)
            self._save_rows("products", new_products)
        except (OSError, ShopError) as exc:
            for kind, original in snapshots.items():
                try:
                    self._path(kind).write_bytes(original)
                except OSError:
                    pass
            raise ShopError(f"Checkout could not finish saving; existing files were restored where possible: {exc}") from exc
        return order

    def list_orders(self, order_id="", customer_id=""):
        order_id, customer_id = str(order_id).strip().upper(), str(customer_id).strip().upper()
        return [o for o in self._read_rows("orders")
                if (not order_id or o["order_id"] == order_id)
                and (not customer_id or o["customer_id"] == customer_id)]

    def order_items(self, order_id):
        code = str(order_id).strip().upper()
        return [i for i in self._read_rows("order_items") if i["order_id"] == code]

    def low_stock(self, threshold=5):
        limit = parse_whole_number(threshold, "Low-stock threshold", allow_zero=True)
        return sorted([p for p in self.list_products() if int(p["stock"]) <= limit],
                      key=lambda p: (int(p["stock"]), p["name"]))

    def report(self):
        orders = self.list_orders()
        return {"order_count": len(orders),
                "order_value": sum((parse_money(o["total"]) for o in orders), Decimal("0.00")),
                "product_count": len(self.list_products()),
                "customer_count": len(self.list_customers())}


def show_products(products):
    if not products:
        print("No matching products found.")
        return
    print(f"{'ID':<7} {'PRODUCT NAME':<34} {'PRICE':>11} {'IN STOCK':>10}")
    print("-" * 66)
    for product in products:
        print(f"{product['product_id']:<7} {product['name'][:34]:<34} "
              f"{currency(product['price']):>11} {product['stock']:>10}")


def show_customers(customers):
    if not customers:
        print("No matching customers found.")
        return
    print(f"{'ID':<7} {'CUSTOMER NAME':<27} {'PHONE':<18} EMAIL")
    print("-" * 76)
    for customer in customers:
        print(f"{customer['customer_id']:<7} {customer['name'][:27]:<27} "
              f"{customer['phone'][:18]:<18} {customer['email']}")


def yes_no(prompt):
    answer = input(prompt + " [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def products_menu(shop):
    while True:
        print("\nMANAGE PRODUCTS\n1. List products\n2. Add product\n3. Update product\n4. Remove product\n0. Back")
        selection = input("Choose: ").strip()
        try:
            if selection == "1":
                show_products(shop.list_products())
            elif selection == "2":
                name = input("Product name: ")
                price = input("Unit price: ")
                stock = input("Quantity in stock: ")
                code = shop.add_product(name, price, stock)
                print(f"Product saved with ID {code}.")
            elif selection == "3":
                code = input("Product ID to update: ").strip().upper()
                item = shop.find_product(code)
                if not item:
                    raise ShopError("Product ID not found.")
                print("Press Enter to keep the current value.")
                name = input(f"Name ({item['name']}): ").strip()
                price = input(f"Price ({item['price']}): ").strip()
                stock = input(f"Stock ({item['stock']}): ").strip()
                shop.update_product(code, name=name if name else None,
                                    price=price if price else None,
                                    stock=stock if stock else None)
                print("Product updated.")
            elif selection == "4":
                code = input("Product ID to remove: ").strip().upper()
                item = shop.find_product(code)
                if not item:
                    raise ShopError("Product ID not found.")
                if yes_no(f"Remove {item['name']} ({code}) from catalogue?"):
                    shop.remove_product(code)
                    print("Product removed. Past order records remain available.")
                else:
                    print("Removal cancelled.")
            elif selection == "0":
                return
            else:
                print("Invalid menu option. Try again.")
        except ShopError as exc:
            print(f"Error: {exc}")


def customers_menu(shop):
    while True:
        print("\nCUSTOMERS\n1. Register customer\n2. List customers\n3. Search customers\n4. Update customer\n5. Remove customer without orders\n0. Back")
        selection = input("Choose: ").strip()
        try:
            if selection == "1":
                name = input("Customer full name: ")
                phone = input("Phone (optional): ")
                email = input("Email (optional): ")
                code = shop.register_customer(name, phone, email)
                print(f"Customer registered with ID {code}.")
            elif selection == "2":
                show_customers(shop.list_customers())
            elif selection == "3":
                query = input("Search customer ID or name: ")
                show_customers(shop.search_customers(query))
            elif selection == "4":
                code = input("Customer ID to update: ").strip().upper()
                customer = shop.find_customer(code)
                if not customer:
                    raise ShopError("Customer ID not found.")
                print("Press Enter to keep a value; enter '-' to clear phone/email.")
                name = input(f"Name ({customer['name']}): ").strip()
                phone = input(f"Phone ({customer['phone']}): ").strip()
                email = input(f"Email ({customer['email']}): ").strip()
                shop.update_customer(code, name=name if name else None,
                                     phone=("" if phone == "-" else phone) if phone else None,
                                     email=("" if email == "-" else email) if email else None)
                print("Customer updated.")
            elif selection == "5":
                code = input("Customer ID to remove: ").strip().upper()
                if yes_no(f"Delete customer {code} (only if no orders exist)?"):
                    shop.remove_customer(code)
                    print("Customer removed.")
                else:
                    print("Removal cancelled.")
            elif selection == "0":
                return
            else:
                print("Invalid menu option. Try again.")
        except ShopError as exc:
            print(f"Error: {exc}")


def show_cart(shop, cart):
    if not cart:
        print("Cart is empty.")
        return
    try:
        lines, total = shop.cart_summary(cart)
    except ShopError as exc:
        print(f"Cart cannot be checked out: {exc}")
        return
    print(f"{'PRODUCT':<33} {'QTY':>5} {'UNIT':>12} {'LINE TOTAL':>14}")
    print("-" * 68)
    for line in lines:
        print(f"{line['product_name'][:33]:<33} {line['quantity']:>5} "
              f"{currency(line['unit_price']):>12} {currency(line['line_total']):>14}")
    print("-" * 68)
    print(f"SUBTOTAL / TOTAL (no taxes or delivery fees): {currency(total)}")


def cart_menu(shop):
    code = input("Enter registered customer ID (e.g., C001): ").strip().upper()
    customer = shop.find_customer(code)
    if not customer:
        print("Customer not found. Register a customer using main menu option 3.")
        return
    print(f"Shopping as {customer['name']} ({code}). No payment details are collected.")
    cart = {}
    while True:
        print("\nSHOPPING CART / SIMULATED CHECKOUT\n1. Add item\n2. View cart & subtotal\n3. Change item quantity\n4. Remove item\n5. Confirm & place order\n0. Back")
        selection = input("Choose: ").strip()
        try:
            if selection == "1":
                product_id = input("Product ID: ").strip().upper()
                quantity = parse_whole_number(input("Quantity to add: "), "Order quantity")
                draft = dict(cart)
                draft[product_id] = draft.get(product_id, 0) + quantity
                shop.cart_summary(draft)  # Do not allow an over-stock item into the cart.
                cart = draft
                print("Item added.")
            elif selection == "2":
                show_cart(shop, cart)
            elif selection == "3":
                product_id = input("Product ID already in cart: ").strip().upper()
                if product_id not in cart:
                    raise ShopError("Product is not in your cart.")
                quantity = parse_whole_number(input("New quantity (greater than zero): "), "Order quantity")
                draft = dict(cart)
                draft[product_id] = quantity
                shop.cart_summary(draft)
                cart = draft
                print("Cart quantity updated.")
            elif selection == "4":
                product_id = input("Product ID to remove from cart: ").strip().upper()
                if product_id not in cart:
                    raise ShopError("Product is not in your cart.")
                del cart[product_id]
                print("Item removed from cart.")
            elif selection == "5":
                if not cart:
                    raise ShopError("Your shopping cart is empty.")
                show_cart(shop, cart)
                if yes_no("Confirm this simulated order? (No money is charged)"):
                    order = shop.place_order(code, cart)
                    print(f"ORDER CONFIRMED: {order['order_id']} | {currency(order['total'])}")
                    print("Stock was updated. Order and order items were saved to CSV.")
                    cart.clear()
                    return
                else:
                    print("Checkout cancelled; cart unchanged.")
            elif selection == "0":
                if cart and not yes_no("Discard the current unconfirmed cart?"):
                    continue
                return
            else:
                print("Invalid menu option. Try again.")
        except ShopError as exc:
            print(f"Error: {exc}")


def order_history_menu(shop):
    print("\nORDER HISTORY\n1. All orders\n2. Search by order ID\n3. Search by customer ID")
    selection = input("Choose: ").strip()
    if selection == "1":
        orders = shop.list_orders()
    elif selection == "2":
        orders = shop.list_orders(order_id=input("Order ID: "))
    elif selection == "3":
        orders = shop.list_orders(customer_id=input("Customer ID: "))
    else:
        print("Invalid menu option.")
        return
    if not orders:
        print("No matching orders found.")
        return
    print(f"{'ORDER':<7} {'CUSTOMER':<24} {'DATE / TIME':<18} {'ITEMS':>5} {'TOTAL':>12}")
    print("-" * 73)
    for order in orders:
        print(f"{order['order_id']:<7} {order['customer_name'][:24]:<24} "
              f"{order['created_at']:<18} {order['item_count']:>5} {currency(order['total']):>12}")
    if len(orders) == 1:
        print("Order items:")
        for item in shop.order_items(orders[0]["order_id"]):
            print(f"  {item['product_name']} | {item['quantity']} x "
                  f"{currency(item['unit_price'])} = {currency(item['line_total'])}")


def reports_menu(shop):
    try:
        limit = input("Low-stock threshold [press Enter for 5]: ").strip()
        threshold = parse_whole_number(limit, "Threshold", allow_zero=True) if limit else 5
        summary = shop.report()
        print("\nBASIC SHOP REPORT")
        print(f"Products in catalogue: {summary['product_count']}")
        print(f"Registered customers: {summary['customer_count']}")
        print(f"Recorded orders: {summary['order_count']}")
        print(f"Total recorded order value: {currency(summary['order_value'])}")
        print(f"\nProducts with stock of {threshold} or fewer:")
        show_products(shop.low_stock(threshold))
    except ShopError as exc:
        print(f"Error: {exc}")


def main():
    parser = argparse.ArgumentParser(description="CampusCart Python console project")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent / "data",
                        help="Optional directory containing CSV files (defaults to ./data)")
    args = parser.parse_args()
    try:
        shop = ShopStore(args.data_dir)
    except (ShopError, OSError) as exc:
        print(f"Startup error: {exc}")
        return 1
    print("\nCAMPUSCART | INFO 301 - PROJECT 3")
    print("Educational CSV-based shop | Simulated checkout only | No real payments")
    try:
        while True:
            print("\nMAIN MENU\n1. View/Search Products\n2. Manage Products\n3. Register/Manage Customer\n4. Shopping Cart / Place Order\n5. View Order History\n6. Basic Reports\n7. Exit")
            choice = input("Select 1-7: ").strip()
            try:
                if choice == "1":
                    query = input("Search ID/name (press Enter to view all): ")
                    show_products(shop.search_products(query))
                elif choice == "2":
                    products_menu(shop)
                elif choice == "3":
                    customers_menu(shop)
                elif choice == "4":
                    cart_menu(shop)
                elif choice == "5":
                    order_history_menu(shop)
                elif choice == "6":
                    reports_menu(shop)
                elif choice == "7":
                    print("Goodbye. All confirmed changes remain in CSV files.")
                    return 0
                else:
                    print("Invalid menu option. Enter a number from 1 to 7.")
            except (OSError, csv.Error) as exc:
                print(f"File error: {exc}")
    except (EOFError, KeyboardInterrupt):
        print("\nSession ended. Confirmed records are saved to CSV.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
