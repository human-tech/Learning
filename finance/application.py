import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.globals.update(usd=usd)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    stats = db.execute("SELECT stock, SUM(number) as number, value, SUM(number*value) AS amount FROM " +
                       session["user_name"]+" GROUP BY stock")
    cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid=session["user_id"])[0]['cash']
    if not stats:
        return render_template("index.html", cash=cash, total=int(cash))
    else:
        return render_template("index.html", stats=stats, cash=cash, total=stats[0]['amount'] + int(cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        stonk = lookup(request.form.get("symbol"))

        if not stonk:
            return apology("stock does not exist", 400)
        elif request.form.get("shares").isalpha():
            return apology("invalid shares", 400)

        shares = float(request.form.get("shares"))
        cash = db.execute("SELECT cash FROM users WHERE id= :userid", userid=session["user_id"])[0]['cash']
        amount = float(request.form.get("shares"))*stonk['price']

        if float(shares) <= 0 or isinstance(shares, int):
            return apology("invalid shares", 400)

        elif float(shares) <= 0 or not shares.is_integer():
            return apology("invalid shares", 400)

        elif amount > cash:
            return apology("not enough cash", 400)

        db.execute("INSERT INTO "+session["user_name"]+" (symbol, stock, number, value) VALUES(?, ?, ?, ?)",
                   request.form.get("symbol"), stonk['name'], shares, stonk['price'])

        # Insert into database
        db.execute("UPDATE users SET cash= :leftover WHERE id= :userid", leftover=cash-amount, userid=session["user_id"])

        # Redirect user to login
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute("SELECT stock, number, value, ABS(number*value) AS amount FROM "+session["user_name"]+"")
    return render_template("history.html", history=history, cash=session["cash"], total=history[0]['amount'] + int(session["cash"]))


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

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

    if request.method == "POST":
        stocks = lookup(request.form.get("symbol"))

        if not stocks:
            return apology("invalid stock", 400)

        return render_template("quoted.html", stocks=stocks)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        rows = db.execute("SELECT username FROM users WHERE username = :username",
                          username=request.form.get("username"))

        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not len(rows) == 0:
            return apology("username already exists", 400)

        elif not password == request.form.get("confirmation"):
            return apology("password does not match", 400)

        elif len(password) < 8:
            return apology("password must contain at least 8 characters", 400)

        elif not re.search('[@_!#$%^&*()<>?/\|}{~:a-zA-Z]', password) or not re.search('[a-zA-Z]', password) or not re.search('[0-9]', password):
            return apology("password must contain a special character, a number and an alphabet", 400)

        username = request.form.get("username")

        # Insert into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(request.form.get("password")))
        db.execute("CREATE TABLE "+username.replace(" ", "")+" (symbol TEXT, stock TEXT, number INT, value INT)")

        # Redirect user to login
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    stocklist = db.execute("SELECT symbol FROM "+session["user_name"]+" GROUP BY symbol")

    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        stonk = lookup(request.form.get("symbol"))
        cash = db.execute("SELECT cash FROM users WHERE id= :userid", userid=session["user_id"])[0]['cash']
        amount = float(shares)*stonk['price']

        # Ensure username was submitted
        sym_test = next((i for i in stocklist if i['symbol'] == symbol), None)

        if sym_test == None:
            return apology("stock does not exist", 400)

        # Ensure password was submitted
        elif shares <= 0 or shares > int(db.execute("SELECT SUM(number) AS number FROM "+session["user_name"]+" WHERE symbol= :sym GROUP BY symbol", sym=symbol)[0]['number']):
            return apology("invalid shares", 400)

        db.execute("INSERT INTO "+session["user_name"]+" (symbol, stock, number, value) VALUES(?, ?, ?, ?)",
                   symbol, stonk['name'], -shares, stonk['price'])

        # Insert into database
        db.execute("UPDATE users SET cash= :leftover WHERE id= :userid", leftover=cash+amount, userid=session["user_id"])

        # Redirect user to index
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", stocklist=stocklist)


@app.route("/chpass", methods=["GET", "POST"])
@login_required
def chpass():
    """Change Password"""

    if request.method == "POST":

        oldpass = db.execute("SELECT hash FROM users WHERE id = :userid",
                             userid=session["user_id"])
        newpass = request.form.get("newpass")

        # Ensure username was submitted
        if not check_password_hash(oldpass[0]["hash"], request.form.get("oldpass")):
            return apology("Old Password does not match", 400)

        # Ensure password was submitted
        elif not request.form.get("newpass"):
            return apology("must provide new password", 400)

        elif not newpass == request.form.get("confirm-password"):
            return apology("password does not match", 400)

        elif len(newpass) < 8:
            return apology("password must contain at least 8 characters", 400)

        elif not re.search('[@_!#$%^&*()<>?/\|}{~:a-zA-Z]', newpass) or not re.search('[a-zA-Z]', newpass) or not re.search('[0-9]', newpass):
            return apology("password must contain a special character, a number and an alphabet", 400)

        # Insert into database
        db.execute("UPDATE users SET hash = :newpass WHERE id = :userid",
                   newpass=generate_password_hash(newpass), userid=session["user_id"])

        # Redirect user to login
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("pass.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
