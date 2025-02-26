# CS50x Finance - Level 02: Buy Functionality

This directory contains the implementation of the "buy" functionality for the CS50x Finance problem set, corresponding to Level 2.

## Overview

This level focuses on allowing users to buy shares of stocks.  It includes input validation, stock lookup, cash balance checks, database updates, and transaction recording.

## Functionality

The "buy" route (`/buy`) handles both GET and POST requests:

*   **GET:** Displays the "buy" form, allowing the user to enter a stock symbol and the number of shares to purchase.
*   **POST:** Processes the purchase request:
    1.  Validates user input (symbol and number of shares).
    2.  Looks up the stock price using the `lookup()` helper function.
    3.  Checks if the user has sufficient cash to complete the transaction.
    4.  Updates the user's cash balance in the `users` table.
    5.  Records the transaction details in the `transactions` table.
    6.  Displays a success message or an error message if the purchase fails.

## Implementation Details

*   **Input Validation:**  The code validates the stock symbol, the number of shares (must be a positive integer), and ensures the stock symbol exists using the `lookup()` function.
*   **Cash Balance Check:** The code verifies that the user has enough cash before processing the purchase.
*   **Database Updates:**  The user's cash balance is updated, and the transaction is recorded in the database using parameterized queries to prevent SQL injection.
*   **Error Handling:**  The code includes error handling to manage cases such as invalid input, insufficient cash, or lookup failures.

## Key Improvements in this Level

*   **Input Validation:**  Added comprehensive input validation to ensure data integrity.
*   **Stock Lookup:**  Integrated the `lookup()` function to retrieve stock prices.
*   **Cash Balance Check:**  Implemented a check to prevent users from buying stocks they can't afford.
*   **Database Updates:**  Added database updates to reflect the purchase and transaction recording.

## Further Improvements (For Later Levels)

*   **Database Transactions:**  Using database transactions to ensure atomicity (all or nothing) for the cash update and transaction insertion.
*   **Rounding:** Rounding the transaction value to prevent floating-point errors.
*   **More Robust Error Handling:**  Adding more specific error handling and logging.

## How to Run

1.  Ensure you have the CS50x Finance environment set up.
2.  Navigate to the project directory.
3.  Run the Flask application (e.g., `flask run`).

## Files Included

*   `app.py`: Contains the Python code for the "buy" route.
*   `buy.html`: The HTML template for the "buy" form.
