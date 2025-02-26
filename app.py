import os
import csv
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd
import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Path to your CSV file
CSV_FILE = "listing_status.csv"

def lookup(symbol):
    """Look up quote for symbol."""

    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:  # Handle potential encoding issues
            reader = csv.DictReader(file)
            for row in reader:
                if row["symbol"].upper() == symbol.upper():  # Case-insensitive comparison
                    try:  # Attempt to convert price to float
                        price = float(row["price"])
                        return {
                            "symbol": row["symbol"],
                            "name": row["name"],
                            "price": price
                        }
                    except ValueError:
                        return None # Price is not a valid float

            return None  # Symbol not found
    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILE}' not found.")  # Print for debugging
        return None
    except Exception as e: # Catch other potential errors
        print(f"An error occurred: {e}")
        return None

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    
    symbol = request.form.get("symbol")
    shares = request.form.get("shares")

    # Validate inputs
    if not symbol or not shares:
        return apology("Must provide both symbol & shares")
    
    # **Level 2: Shares Validation**
    symbol = symbol.upper()
    try:
        shares = int(shares)
    except ValueError:
        return apology("Shares must be a valid integer")
    if shares <= 0:
        return apology("Shares must be a positive integer")

    # **Level 3: Stock Symbol Validation**    
    stock = lookup(symbol)
    if stock is None:
        return apology("Symbol not found!")
    
    # **Level 4: Calculate Transaction Value**
    # transaction_value = shares * stock["price"]
    transaction_value = round(shares * stock["price"], 2)
    
    # **Level 5: Check User's Cash Balance**
    user_id = session["user_id"] #to get current user
    user_cash_result = db.execute("SELECT cash from users WHERE id = ?", user_id)
    #if you want to see what user_id returns then write:
    # return jsonify(user_cash_result)
    # outputs a list: [{"cash":10000}]
    """
    #Here we can Create transactions table in finance.db
    CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price REAL NOT NULL,
    transaction DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    if not user_cash_result or user_cash_result[0]["cash"] is None:
        return apology("User cash not found!")

    user_cash = user_cash_result[0]["cash"]

    # Check if the user has enough cash
    # if (current user cash) < transaction_value return apology
    if user_cash < transaction_value:
        return apology("Not enough Cash!")
    
    # **Level 6: Update new balance in Database**
    # Update user's cash balance
    new_balance = user_cash - transaction_value
    
    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

    #**Level 7: adding data into transactions db table
    """
    it's generally better to store timestamps in UTC.  This avoids timezone issues.  You can use:
    datetime.datetime.utcnow()
    """
    date = datetime.datetime.now()

    db.execute('INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)', user_id, stock["symbol"], shares, stock["price"], date)
    """Currently, the cash update and the transaction insertion are separate operations. If one fails, you could end up with inconsistent data (e.g., cash deducted but no transaction recorded).  Transactions ensure atomicity (all or nothing), consistency, isolation, and durability (ACID properties).  In SQLite, you can use conn.execute("BEGIN TRANSACTION") and conn.execute("COMMIT") (or conn.execute("ROLLBACK") if an error occurs).
    # Database transaction
    try:
        db.execute("BEGIN TRANSACTION")  # Start transaction
        # Deduct user cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", (new_balance, user_id)) # Parameterized query
        date = datetime.datetime.utcnow()  # UTC timestamp
        # Record the transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction) VALUES (?, ?, ?, ?, ?)", (user_id, stock["symbol"], shares, stock["price"], date)) # Parameterized query
        db.execute("COMMIT")  # Commit transaction
    except Exception as e:  # Catch database errors
        db.execute("ROLLBACK")  # Rollback on error
        print(f"Database error: {e}")  # Log the error (important!)
        return apology("An error occurred during the transaction.")  # User-friendly message
    """
    flash("Bought successful!")

    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
            # rows[0]["hash"] refers to the hashed password stored in the database for the user.
            # rows is a list of dictionaries.
            # rows[0] accesses the first dictionary (i.e., the first row) in the list.
            # rows[0]["hash"] accesses the value associated with the "hash" key in the first dictionary.
            # If you were to use rows["hash"], it would result in an error because rows is a list, not a dictionary, and lists do not have keys.
            # [
            #     {
            #         "id": 1,
            #         "username": "john_doe",
            #         "hash": "hashed_password_string",
            #         "cash": 10000.00
            #     }
            # ]
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
  POPULAR_STOCKS = [
        "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
        "NVDA", "JPM", "JNJ", "V", "PG",
        "UNH", "XOM", "NFLX", "META", "WMT",
        "DIS", "BAC", "HD", "PFE", "KO"
    ]
  
  if request.method == "POST":
    symbol = request.form.get("symbol")

    if not symbol:
      flash("Must provide symbol")  # Use flash instead of apology
      return render_template("quote.html", popular_stocks=POPULAR_STOCKS)

    quote_data = lookup(symbol)  # Call lookup function

    if not quote_data:
      flash("Invalid symbol or could not retrieve quote.")
      return render_template("quote.html", popular_stocks=POPULAR_STOCKS)

    name = quote_data.get("name")  # Assuming name is also retrieved by lookup
    price = quote_data["price"]
    symbol = quote_data["symbol"].upper()

    return render_template("quoted.html", name=name, price=price, symbol=symbol)

  else:
    return render_template("quote.html", popular_stocks=POPULAR_STOCKS)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    # Get form inputs
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirmation')

    # Validate inputs
    if not username or not password or not confirm:
        return apology(f"Missing {'Username' if not username else 'Password' if not password else 'Confirmation'}")
    
    if password != confirm:
        return apology("Passwords do not match!")

    # Check if username already exists
    existing_user = db.execute('SELECT * FROM users WHERE username = ?', username)
    if existing_user:
        return apology("Username already exists!")

    # Hash the password
    hash = generate_password_hash(password)

    # Insert new user into the database
    try:
        db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', username, hash)
    except:
        return apology("Error inserting user. Please try again!")

    # Remember which user has logged in by storing their user ID in the session
    # Retrieve user ID and log them in
    user_id = db.execute('SELECT id FROM users WHERE username = ?', username)
    session["user_id"] = user_id[0]["id"]

    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
