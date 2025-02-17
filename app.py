import os
import csv
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from functools import lru_cache

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Cache for lookup function to reduce API calls
@lru_cache(maxsize=100)  # Cache up to 100 stock lookups
def cached_lookup(symbol):
    """Cached version of the stock lookup function."""
    return lookup(symbol)

# Gemini: Load stock data from CSV
stock_data = []
with open("listing_status.csv", "r", encoding="utf-8") as file: # Add encoding if needed
    reader = csv.DictReader(file)
    for row in reader:
        try:
            row['price'] = float(row['price']) if 'price' in row and row['price'] else None #convert price to float if exist
            stock_data.append(row)
        except ValueError:
            print(f"Skipping invalid price in row: {row}")

def lookup(symbol):
    """Look up quote for symbol in local CSV data."""
    symbol = symbol.upper()
    for stock in stock_data:
        if stock['symbol'].upper() == symbol:
            return stock
    return None  # Return None if symbol not found

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks with pagination and caching."""
    user_id = session["user_id"]

    # Fetch user cash balance
    cash_data = db.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    if not cash_data:
        return apology("User not found.", 404)
    cash = cash_data[0]["cash"]

    # Fetch user's transactions grouped by symbol
    transactions = db.execute(
        "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
        (user_id,)
    )

    # Pagination: Get current page from query string, default is 1
    page = int(request.args.get("page", 1))
    items_per_page = 10
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    portfolio = []
    total_shares_value = 0

    # Calculate total value of each holding and the overall portfolio
    for transaction in transactions[start_index:end_index]:  # Apply pagination
        stock = cached_lookup(transaction["symbol"])
        if not stock:
            continue
        price = stock["price"]
        total = transaction["shares"] * price
        total_shares_value += total
        portfolio.append({
            "symbol": transaction["symbol"],
            "shares": transaction["shares"],
            "price": price,
            "total": total
        })

    # Fetch username for the welcome message
    user_data = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = user_data[0]["username"].capitalize() if user_data else "User"

    # Calculate grand total
    grand_total = total_shares_value + cash

    # Pagination helpers
    total_items = len(transactions)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    has_next = page < total_pages
    has_previous = page > 1

    return render_template(
        "index.html",
        database=portfolio,
        cash=cash,
        username=username,
        grand_total=grand_total,
        page=page,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous
    )

    # """Show portfolio of stocks."""
    # user_id = session["user_id"]

    # # Fetch user cash balance
    # cash_data = db.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    # if not cash_data:
    #     return apology("User not found.", 404)
    # cash = cash_data[0]["cash"]

    # # Fetch user's transactions grouped by symbol
    # transactions = db.execute(
    #     "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
    #     (user_id,)
    # )

    # portfolio = []
    # total_shares_value = 0

    # # Calculate total value of each holding and the overall portfolio
    # for transaction in transactions:
    #     stock = lookup(transaction["symbol"])
    #     if not stock:
    #         continue
    #     price = stock["price"]
    #     total = transaction["shares"] * price
    #     total_shares_value += total
    #     portfolio.append({
    #         "symbol": transaction["symbol"],
    #         "shares": transaction["shares"],
    #         "price": price,
    #         "total": total
    #     })

    # # Fetch username for the welcome message
    # user_data = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    # username = user_data[0]["username"].capitalize() if user_data else "User"

    # # Calculate grand total
    # grand_total = total_shares_value + cash

    # return render_template(
    #     "index.html",
    #     database=portfolio,
    #     cash=cash,
    #     username=username,
    #     grand_total=grand_total
    # )

# @app.route("/")
# @login_required
# def index():
#     """Show portfolio of stocks"""
#     user_id = session["user_id"]

#     transactions_db = db.execute("SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
#     cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
#     cash = cash_db[0]["cash"]
#     # Adding Welcome username
#     user_db = db.execute("SELECT username FROM users WHERE id = ?", user_id)
#     username = user_db[0]["username"].capitalize()

#     total_shares_value = sum(row["shares"] * row["price"] for row in transactions_db)

#     return render_template("index.html", database = transactions_db, cash = cash, username=username, total_shares_value=total_shares_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    
    else:  # POST method: Handle the purchase
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        
        if not symbol:
            return apology("Must give Symbol!")
        
        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Symbol does not Exist!")
        
        # Validate shares
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Shares must be a positive integer!", 400)

        shares = int(shares)

        # logic to handle the purchase
        transaction_value = shares * stock["price"]
        user_id = session["user_id"]
        # Get user's cash balance
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
        user_cash = user_cash_db[0]["cash"]

        if user_cash < transaction_value:
            return apology("Not enough money to complete the purchase!")

        # Update user's cash and add transaction record
        uptd_cash = user_cash - transaction_value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        date = datetime.datetime.now()
        
        # Add a new transaction record to the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES(?, ?, ?, ?, ?)", user_id, stock["symbol"], shares, stock["price"], date)

        flash("Bought!")
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    # Fetch transaction history for the user
    transactions = db.execute(
        "SELECT symbol, shares, price, date FROM transactions WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )

    # Fetch the current cash balance of the user
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    cash = user_cash[0]["cash"] if user_cash else 0

    return render_template("history.html", transactions=transactions, cash=cash)
# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""
#     user_id = session["user_id"]
    
#     transactions_db = db.execute("SELECT * FROM transactions WHERE user_id = :id", id=user_id)

#     cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
#     cash = cash_db[0]["cash"]

#     return render_template("history.html", transactions = transactions_db, cash = cash)

@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Allow user to add cash to their account"""
    if request.method == "GET":
        return render_template("add.html")

    elif request.method == "POST":
        try:
            # Validate user input
            new_cash = request.form.get("new_cash")
            if not new_cash or int(new_cash) <= 0:
                return apology("Please enter a valid amount to add.")
            
            new_cash = int(new_cash)
        except ValueError:
            return apology("Invalid amount entered!")

        # Update user's cash balance
        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", new_cash, user_id)

        flash("Cash added successfully!")
        return redirect("/")
# @app.route("/add_cash", methods=["GET", "POST"])
# @login_required
# def add_cash():
#     """User can add cash"""
#     if request.method == "GET":
#         return render_template("add.html")
#     else:
#         new_cash = int(request.form.get("new_cash"))

#         if not new_cash:
#             return apology("You must Give Money")
        
#         user_id = session["user_id"]
#         user_cash_db = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)
#         user_cash = user_cash_db[0]["cash"]

#         uptd_cash = user_cash + new_cash
        
#         db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

#         return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    
    else: # No need for else
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Must give Symbol!", 400)
        
        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Symbol does not Exist!", 404)
        
        return render_template("quoted.html", stock=stock)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    
# No need for else:
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

# if not username or not password or not confirmation:
        # return apology(f"Missing { 'username' if not username else 'password' if not password else 'confirmation' }")
        if not username:
            return apology("Must give a Username")
        if not password:
            return apology("Must provide a Password")
        if not confirmation:
            return apology("Must give Confirmation")
        if password != confirmation:
            return apology("Passwords do not match")
        
        hash = generate_password_hash(password)

        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        except:
            return apology("Username already exist!")
        # except Exception as e:
        # print(f"Error: {e}")
        # return apology("Username already exists!", 400)
        
        session["user_id"] = new_user

        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "GET":
        # Fetch user's owned stocks with shares > 0
        symbols_user = db.execute(
            "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
            (user_id,)
        )
        symbols = [row["symbol"] for row in symbols_user]

        # Render sell form
        return render_template("sell.html", symbols=symbols)

    elif request.method == "POST":
        # Retrieve form inputs
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Input validation
        if not symbol:
            return apology("Must select a stock symbol!")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Must provide a positive integer number of shares!")

        shares = int(shares)

        # Validate stock symbol using lookup
        stock = lookup(symbol.upper())
        if stock is None:
            return apology("Invalid stock symbol!")

        # Fetch user's current shares for the selected stock
        user_shares_data = db.execute(
            "SELECT SUM(shares) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ?",
            user_id, symbol
        )
        total_shares = user_shares_data[0]["total_shares"] or 0

        if shares > total_shares:
            return apology("Insufficient shares to sell!")

        # Calculate transaction value
        transaction_value = shares * stock["price"]

        # Update user's cash balance
        db.execute(
            "UPDATE users SET cash = cash + ? WHERE id = ?",
            transaction_value, user_id
        )

        # Record the sell transaction in the transactions table
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)",
            user_id, symbol.upper(), -shares, stock["price"], datetime.datetime.now()
        )

        flash("Sold successfully!")
        return redirect("/")