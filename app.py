import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
    return apology("TODO")


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

    stock = lookup(symbol)  # Call lookup function

    if not stock:
      flash("Invalid symbol or could not retrieve quote.")
      return render_template("quote.html", popular_stocks=POPULAR_STOCKS)

    name = stock("name")
    price = stock["price"]
    symbol = stock["symbol"].upper()

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
