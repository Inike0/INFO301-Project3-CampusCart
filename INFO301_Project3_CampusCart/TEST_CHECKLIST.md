# INFO 301 Project 3 - Test Checklist

**Application:** CampusCart (Python console e-commerce simulation)  
**Test command:** `python -m unittest discover -s tests -v`  
**Automated result:** 30 tests passed during project preparation. Rerun before final submission.

Use a **practice copy** of `data/` when performing the write/delete cases below.

| # | Test | Steps or input | Expected result |
|---|---|---|---|
| 01 | List products | Main 1, blank search | Catalogue rows display with IDs, prices, and stock |
| 02 | Valid product addition | Main 2 > 2; name `Lab Book`, price `5.25`, stock `8` | New unique product ID appears in list and CSV |
| 03 | Search existing record | Main 1; search `P009` or `USB` | Matching records display |
| 04 | Search missing record | Main 1; search `P999` | `No matching products found` without crash |
| 05 | Update stock/price | Main 2 > 3; update a practice product | Revised record appears and persists in products.csv |
| 06 | Remove product | Main 2 > 4, confirm `y` | Product disappears from current catalogue |
| 07 | Register customer | Main 3 > 1; valid name and optional contact | New `C...` ID is created and saved |
| 08 | Reject empty name | Add a product with blank name | Friendly error; no row added |
| 09 | Reject negative price | Add product with `-2` price | Friendly error; no row added |
| 10 | Reject decimal stock | Add product with `2.5` units | Friendly error; no row added |
| 11 | Reject zero cart quantity | Main 4 > 1; quantity `0` | Friendly error; item not added |
| 12 | Reject nonnumeric quantity | Quantity `abc` or `1.5` | Friendly error; no crash |
| 13 | Reject insufficient stock | Add quantity greater than available | Error identifies stock limit; no order saved |
| 14 | Correct subtotal calculation | Add 2 units at $2.25 and 3 at $3.10 | Subtotal is exactly **$13.80** |
| 15 | Cancel simulated checkout | Main 4 > 5; reply `n` | No order created; cart remains for editing |
| 16 | Confirm simulated checkout | Add item(s), then Main 4 > 5 > `y` | Unique order ID; orders + items CSV saved; stock reduced |
| 17 | Search order history | Main 5 > 2; enter new order ID | Correct order and item details are listed |
| 18 | Search by customer | Main 5 > 3; enter customer ID | Only that customer's orders display |
| 19 | Low-stock report | Main 6; Enter for threshold 5 | Low-stock items, number and total value of orders shown |
| 20 | Persistence after restart | Exit (7), reopen, search new order/product | Confirmed changes remain available in CSV |
| 21 | Missing CSV creation | In new empty practice directory, run program | CSV files created automatically with headers |
| 22 | Safe customer removal | Try removing a customer who has orders | Removal refused to preserve order history |
| 23 | No payment handling | Perform checkout | No credit/debit card fields or gateway connection |
| 24 | Invalid menu choice | Enter `99`, `abc` | Helpful error; menu displayed again |
| 25 | Normal exit | Main 7 | Clean exit; records still stored |

**Automated tests cover:** CSV setup, unique IDs, product CRUD, customer CRUD, invalid prices, invalid quantities, searching, exact decimal totals, stock reduction, checkout history, low-stock reports, restart persistence, historical snapshots and missing/wrong headers.

**Observation notes for class:** Write down the latest order ID, total, stock before, and stock after a successful checkout. Show both CSV files and the results of restarting the app.
