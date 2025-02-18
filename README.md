# Finance Web Application
This web application allows users to manage their stock portfolios, buy and sell stocks, and track their transaction history.  It is built as part of the CS50x Problem Set 9 using Flask.

## Technologies Used
*   Python
*   Flask
*   SQL (SQLite)
*   HTML
*   CSS
*   JavaScript

## Installation
1.  Clone the repository: `git clone https://github.com/myhifi/Finance_Pset9.git`
2.  Navigate to the project directory: `cd Finance_Pset9`
3.  Create a virtual environment: `python3 -m venv .venv` (or `python -m venv .venv` depending on your setup)
4.  Activate the virtual environment:
    *   Windows: `.venv\Scripts\activate`
    *   macOS/Linux: `source .venv/bin/activate`
5.  Install dependencies: `pip install -r requirements.txt`
6.  Set up the database: (Add any specific database setup steps here)
7.  Run the Flask application: `flask run`

## Usage Instructions
1.  Register a new user account.
2.  Use the "Quote" feature to look up stock prices.
3.  Buy and sell stocks through the respective forms.
4.  View your current portfolio and transaction history.

## Project Structure
The project is organized into levels, with each level implemented on a separate Git branch:

*   **Level 1: Authentication (level01_register_quote branch)**
    *   Implemented user registration, including form validation and password hashing.
    *   Added user login functionality.
    *   Developed the quote functionality to retrieve stock prices from an external API.

*   **Level 2: Buy Transactions (level02_buy branch)**
    *   Implemented buy transactions, handling both whole and fractional shares.

*   **Level 3: Sell Transactions (level03_sell branch)**
    *   Developed sell transactions, including validation and portfolio updates.

*   **Level 4: Portfolio View (level04_portfolio branch)**
    *   Developed the portfolio view, displaying current holdings and balances.

*   **Level 5: Transaction History (level05_history branch)**
    *   Created the transaction history page, showing a record of all buy and sell transactions.

## Acknowledgements
CS50x solving Finance problem Set of week 9 (Flask)
