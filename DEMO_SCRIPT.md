# Group Presentation & Live Demonstration Guide

**INFO 301 | Semester 2, 2026 | Project 3: E-commerce Application**  
**Suggested delivery:** 8-12 minutes, followed by instructor questions. The speaker labels below are **roles**, not assigned group member names.

## Speaker 1 - Introduction (1 minute)

> Good day, lecturer and classmates. Our project is CampusCart, a small Python e-commerce application that works entirely in the terminal. Its goal is to demonstrate programming fundamentals and CSV file storage, not to create a real online store. We will show how products, customers, carts, orders, and reports work together.

Describe: Python 3, no SQL, no GUI, no internet requirement, no real payment processing.

## Speaker 2 - Program structure and data (1.5 minutes)

> Our main file is `app.py`. The `ShopStore` class performs the shopping operations while console functions collect user input and display results. The data is stored in four CSV files: products, customers, orders, and order items. Each CSV has a heading row. We provided over 30 fictional records, including 30 example orders.

Show the project directory and, if available, open the CSV headers. Explain the relationship `orders.order_id -> order_items.order_id` and `orders.customer_id -> customers.customer_id`.

## Speaker 3 - Product and customer workflow (2 minutes)

1. In the terminal, run `python app.py`.
2. Choose **1** and search for **USB**. Explain case-insensitive product search.
3. Choose **2**, then **2**. Add `Lab Book`, price `5.25`, stock `8`; observe the new product ID. (Use a practice copy if you need to preserve original files.)
4. Choose **3**, then **1**. Register `Practice Student`; take note of the returned customer ID.

> Product IDs and customer IDs are automatically generated so records are not confused with one another. The program also checks that product prices and stock values are valid.

## Speaker 4 - Shopping cart and checkout (2 minutes)

1. Main **4** -> enter the newly registered customer ID.
2. Cart **1** -> product `P009` -> quantity `2`.
3. Cart **2** -> explain `unit price x quantity = line total` and that subtotal is the sum of all lines.
4. Cart **5** -> reply `y` to confirm the **simulated** checkout.
5. Write down the generated order ID and amount. Demonstrate that product stock has reduced.

> The program validates stock before allowing the order. Once confirmed, it records the order and every line item separately, and then updates the stock. It never asks for card numbers or charges money.

## Speaker 5 - Reports, tests, persistence, conclusion (2-3 minutes)

1. Main **5**, then **2** -> search the new order ID; show its items.
2. Main **6** -> press Enter -> show order count, recorded order value, and stock at or below five.
3. Main **7** -> exit, restart, and retrieve the new order (records persisted to CSV).
4. Run `python -m unittest discover -s tests -v` in a second terminal, if practical.

> The project was tested for invalid quantities, negative prices, insufficient stock, order totals, and restart persistence. Its main limitation is that it is a single-user CSV prototype rather than a commercial e-commerce service.

## Quick example the instructor can ask you to calculate

- Notebook: $2.25 x 2 = **$4.50**
- Pen: $3.10 x 3 = **$9.30**
- Grand total = **$13.80**
- If a product's stock is 10 and 2 are sold, new stock = **8**.

## Likely questions and prepared answers

**Why use CSV rather than SQL?** The assignment requires a simple CSV-backed program to practice reading and writing structured files with Python's built-in `csv` module.

**What is the difference between `orders.csv` and `order_items.csv`?** `orders.csv` has one row per order (who/when/total); `order_items.csv` stores each product, price and quantity within that order.

**What happens if someone orders more than available stock?** `cart_summary` validates every requested quantity and raises a readable error before saving the order.

**How do you avoid floating-point rounding errors?** Prices and totals use `decimal.Decimal` and are stored with two decimal places.

**Do past orders disappear when a product is deleted?** No. The order-items file retains the purchased product's recorded name, price and quantity.

**What happens on restart?** The app reads the same CSV files again, so confirmed orders and stock changes remain saved.

**Does it process real payments?** No. This is an educational simulation, with no card storage, payment services, or delivery APIs.
