# CampusCart - INFO 301 Final Project (Project 3)

**Project type:** E-commerce Application (educational Python console program)  
**Course:** INFO 301, Semester 2, 2026  
**Interface:** numbered terminal/console menu  
**Storage:** CSV files through Python's built-in `csv` module  
**Payments/deliveries:** SIMULATED ONLY. No card data, actual payment, or delivery services.

## 1. What this program does

CampusCart is a small console shopping application. It allows staff to manage products, register customers, add products to a temporary shopping cart, calculate totals, and confirm simulated orders. Orders are given unique IDs, saved with their line items in CSV files, and deducted from product stock. Users can search order history and view low-stock and sales-value reports.

The design deliberately uses **lists, dictionaries, loops, functions, `decimal.Decimal`, and CSV files**. It does not use a graphical interface, SQL, external APIs, or third-party packages.

## 2. Requirements

- Python **3.8 or later** (Python 3 only)
- A terminal such as Windows Command Prompt, PowerShell, macOS Terminal, or Linux terminal
- No internet connection or Python package installation is required

## 3. How to run the program

1. Download or extract the `INFO301_Project3_CampusCart` folder.
2. Open a terminal inside that folder (where `app.py` is located).
3. Run the command:

```bash
python app.py
```

If your system uses `python3` instead of `python`, run:

```bash
python3 app.py
```

4. Enter a number from **1 to 7** at the main menu. Select **7** to exit.

On Windows, if Python is installed with the launcher, `py app.py` can also be used.

### Safe practice mode (optional)

The included files in `data/` contain example records. To avoid changing them while rehearsing, first copy the `data` folder to another location. Then run:

```bash
python app.py --data-dir /path/to/your/copy
```

The program creates the four CSV files with correct column headers if they do not exist. It never assumes they already have records. If an existing CSV has the wrong header, it stops with an explanation instead of overwriting the file.

## 4. Main menu

| Option | Action |
|---|---|
| 1 | View all products or search by product ID/name |
| 2 | Add, list, update and remove products |
| 3 | Register, list, search, update and (where safe) remove customers |
| 4 | Add cart items, view subtotal, change quantities, remove items, confirm simulated checkout |
| 5 | View all orders or filter by order ID/customer ID |
| 6 | View low-stock products, order count and total recorded order value |
| 7 | Exit safely |

To place an order, **register a customer first** (or use one of the fictional customers already saved). Example IDs include `C001` and `P009`. The checkout option will only save an order after you confirm it.

## 5. Files and folder structure

```text
INFO301_Project3_CampusCart/
|-- app.py                   Main Python console application
|-- README.md                This file
|-- TEST_CHECKLIST.md        Manual normal / invalid-input tests
|-- DEMO_SCRIPT.md           Short presentation and live-demo steps
|-- GITHUB_SUBMISSION.md     GitHub and submission instructions
|-- tests/
|   `-- test_app.py          Automated Python unittest cases
|-- data/
|   |-- products.csv         Current catalogue and stock
|   |-- customers.csv        Registered customer records
|   |-- orders.csv           Order headers, IDs, totals and dates
|   `-- order_items.csv      Items within each order
`-- docs/
    |-- PROJECT_REPORT.docx  Project documentation for instructor
    |-- CLASS_PRESENTATION.pdf  Classroom presentation
    `-- DEMO_OUTPUT.txt      Recorded example run
```

## 6. CSV column meanings

| File | Fields |
|---|---|
| `products.csv` | `product_id`, `name`, `price`, `stock` |
| `customers.csv` | `customer_id`, `name`, `phone`, `email` |
| `orders.csv` | `order_id`, `customer_id`, `customer_name`, `created_at`, `total`, `item_count` |
| `order_items.csv` | `order_id`, `product_id`, `product_name`, `unit_price`, `quantity`, `line_total` |

- IDs are automatically assigned, with prefixes `P`, `C`, and `O`, and must be unique within their corresponding records.
- Prices and totals are stored to **two decimal places**; `Decimal` is used for accurate monetary calculations.
- `item_count` counts **total units purchased**, not distinct product types.
- Order `created_at` is recorded as `YYYY-MM-DD HH:MM` using the computer's local time.
- Old order items preserve the product name and price that were recorded at checkout; later catalogue changes do not rewrite history.
- Cart contents exist only during the current cart session. Leaving an unconfirmed cart discards it after user confirmation.

## 7. Included fictional data

| Record type | Starting record count |
|---|---:|
| Products | 36 |
| Customers | 32 |
| Orders | 30 |
| Order line items | 60 |

All customer names, email addresses, and phone numbers are **fictional demonstration data**. Email addresses use `example.com`; the phone values are placeholders. The old orders are simulated and are provided so order history and summary reports can be demonstrated before a new checkout. No real money has been paid.

## 8. Business rules and validation

1. Product, customer and order IDs are unique; the program automatically generates them.
2. Product names and customer names must not be blank.
3. Price must be **zero or greater**, with no more than two decimal places.
4. Product stock must be a whole number, zero or greater.
5. A shopping-cart item quantity must be a whole number **greater than zero**.
6. The sum of cart quantities cannot exceed available product stock.
7. Checkout requires an existing customer, a nonempty cart, and affirmative confirmation.
8. A checkout stores the order in `orders.csv`, saves its products in `order_items.csv`, and deducts stock in `products.csv`.
9. Removing a customer with existing orders is blocked to preserve historical relationships.
10. The program never asks for card numbers or connects to payment or delivery services.

**Total calculation**: `line_total = unit_price x quantity`; `total = sum(line_total)` across all cart items. No sales tax, service charge or delivery cost is included in this classroom model, so **subtotal equals total**.

## 9. How to test it

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The test suite checks records, validation, searching, persistence, totals, checkout, order history, reports, and safe deletion. See `TEST_CHECKLIST.md` for the steps to show the lecturer during the live demonstration.

## 10. Short demo example

- Main menu **1** -> search `USB` -> see matching products.
- Main menu **3** -> **1** -> register `Practice Student` -> note the returned customer ID.
- Main menu **4** -> enter the customer ID -> **1** -> `P009` -> `2` -> **2** to display cart subtotal -> **5** -> `y` to confirm.
- Main menu **5** -> **2** -> enter the new order ID to view its items.
- Main menu **6** -> press Enter for the default threshold of 5 -> see order count/value and low-stock products.
- Main menu **7** -> exit, restart, and check that the new order remains.

For a complete speaking guide, see `DEMO_SCRIPT.md`.

## 11. Known limitations

- Educational prototype only; one console user at a time.
- CSV provides basic file persistence, **not** a production database or full multi-file transaction guarantees. The checkout attempts to restore prior files if a save fails, but a system crash during multiple writes can still leave inconsistent files.
- No login or permission controls; all actions are available to the console user.
- No tax, discount, delivery calculation, refund processing or real payment functionality.
- Customer phone/email formats are demonstration-level checks, not full identity verification.
- Dates use the local computer clock, not an authenticated server time source.

## 12. Submission checklist

- [ ] Review that `app.py` runs with Python 3.
- [ ] Include all four CSV data files (already 30+ records in multiple datasets).
- [ ] Include `README.md`, `TEST_CHECKLIST.md` and demo materials.
- [ ] Show an actual simulated checkout and restart-persistence demonstration.
- [ ] Push the project folder to your group's own GitHub repository.
- [ ] Email the GitHub link and group information to **gdolokelen@gmail.com** by **November 19, 2026, 11:59 PM**.
- [ ] Prepare for the **November 21, 2026** class presentation.

**Submission status:** Project files are provided here; GitHub upload and email transmission must still be performed from a group member's account.
