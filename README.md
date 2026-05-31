C$50 Finance 📈
A robust, full-stack web application designed to simulate a stock trading platform. Users can register for an account, check real-time stock quotes, simulate buying and selling stocks with mock currency, track their active portfolios, and monitor stock price thresholds using a custom algorithmic watchlist.

This project was built as part of CS50x Problem Set 9, with several custom features implemented beyond the base specifications.  

🚀 Features
Core Capabilities
User Authentication: Secure user registration, login, and logout tracking handled via Flask session management. Passwords are safe and encrypted using cryptographic hashing algorithms.  

Real-Time Quotes: Fetches live stock data (company name, ticker symbol, and current market price) dynamically via the CS50 Finance API.  

Simulated Trading: Users can buy and sell stock shares. The application automatically checks for proper formatting, verifies positive integer inputs, balances transaction totals against available cash, and updates the local database immediately.  

Dynamic Portfolio Dashboard (Index): Displays a detailed breakdown of the user's currently owned stocks, total share aggregates, live valuations, cash reserves, and a grand total value. Quick-action buy/sell forms are built directly into the table rows.  

Transaction History Ledger: Provides an immutable, timestamped ledger of every stock transaction (purchases and sales) completed by the user.  

Custom Enhancements
Interactive Stock Watchlist: A personalized stock tracker where users can save specific tickers alongside target prices and trigger rules (Above or Below).  

Live Status Evaluation: The application cross-references target prices with live stock lookups to display a dynamic threshold alert (✅ or -).  

Inline Editing & Deletion: Includes full CRUD operations, allowing users to modify target rules and prices inline or completely purge entries without leaving the view.  

Add Funds (Add Cash): A simple portal letting users mock-deposit extra money into their portfolio to expand their trading power.  

Account Security Manager (Change Password): A self-contained security route requiring old-password verification, preventing users from reusing their current password, and enforcing strict password confirmation matches.  

🛠️ Tech Stack
Backend Framework: Python with Flask  

Session State: Flask-Session (filesystem-backed cache storage)  

Database Management: SQLite handled via the CS50 SQL engine  

Security Processing: Werkzeug (generate_password_hash & check_password_hash)  

Frontend UI: Jinja2 Template Engine, HTML5, CSS3, and Bootstrap 5  

📂 Project Architecture
Based on the packed file system in Finance New.txt, the workspace layout is structured as follows:  

    ```Plaintext
    ├── app.py             # Main routing controller, API endpoints, and core execution logic
    ├── helpers.py         # Middleware tools (login requirements, USD formatting, custom apologies)
    ├── finance.db         # Core relational SQLite database (users, transactions, watchlist)
    ├── requirements.txt   # Declared environmental package dependencies
    ├── static/            # Static UI asserts (custom styling stylesheets and design icons)
    │   ├── favicon.ico
    │   └── styles.css
    └── templates/         # Modular Jinja2 web interface templates
        ├── layout.html    # Core global navigation layout structure
        ├── index.html     # Active trading dashboard interface
        ├── watchlist.html # Watchlist management portal
        └── [..other interface elements..]

💾 Database Schema
The persistent engine utilizes three primary relational tables within finance.db to link financial datasets together:  

1. users
Tracks user credential hashes and currently held liquid asset valuations.  

2. transactions
Logs all incoming buy and outgoing sell events. Sell quantities are systematically logged as negative integers to simplify arithmetic balance queries.  

3. watchlist
Maintains specialized alert settings linked directly to target price constraints and direction conditionals mapped to individual user accounts.  

⚙️ Installation & Local Setup
Clone the Repository:

git clone https://github.com/yourusername/Finance_Pset9.git
cd Finance_Pset9

2.  **Establish a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install Application Dependencies:

pip install -r requirements.txt

4.  **Launch the Web Server:**
    ```bash
    flask run
Open your web browser and navigate to `[http://127.0.0.1:5000/](http://127.0.0.1:5000/)` to test your platform.
