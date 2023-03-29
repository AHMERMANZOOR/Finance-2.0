# Importing all libraries
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime
from time import time

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
 
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
now = datetime.now()


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance-2.0.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Index page/Start-up page
@app.route("/")
def index():
    """Showing user the opening page of our website"""
    if session.get('user_id') is not None:
        return redirect('/home')
    return render_template("index.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Register page
@app.route("/register", methods=["GET","POST"])
def register():
    """Showing user the register page and asking for credentials"""
    # Forget any user_id
    session.clear()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        confirmation = request.form.get("confirmation")
        password = request.form.get("password")
        email = request.form.get("email")
        check = db.execute("SELECT * FROM registration;")
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensuring that the username is unique
        if len(check) != 0:
            check = db.execute("SELECT id FROM registration WHERE user_name = ?;", request.form.get("username"))
            if len(check) != 0:
                return apology("Username already exists", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)
        
        # Ensure email was submitted
        if not email:
            return apology("must provide a password", 400)

        # Confirming that confirmation is not empty
        if not confirmation:
            return apology("must provide password again", 400)

        # Confirming that confirmation is equal to password
        if confirmation != password:
            return apology("The password doesn't match", 400)

        # Adding the user to the Database
        password_hash = str(generate_password_hash(password))
        db.execute("INSERT INTO registration(user_name,password_hash,email_address,cash) VALUES(?,?,?,?)", request.form.get("username"), password_hash,email,100)

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


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
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM registration WHERE user_name = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/home")
@login_required
def home():
    """Show portfolio of stocks"""
    purchase_data = db.execute("SELECT * FROM Share WHERE user_id = ?;", session["user_id"])
    user = db.execute("SELECT cash FROM registration WHERE id = ?;", session["user_id"])
    totalSharePrice = 0
    current_price = []
    name = []
    total_user = user[0]["cash"]
    print(user)
    for data in purchase_data:
        data1 = lookup(data["comp_name"])
        name.append(data1["Symbol"])
        current_price.append(data1["Price"])
        totalSharePrice += data1["Price"]
        total_user += data1["Price"]
    return render_template("index.html", data=purchase_data, price=current_price, name=name, cash=user,grand_total=total_user, totalSharePrice=totalSharePrice)


@app.route("/company", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Calling lookup function
        data = lookup(request.form.get("symbol").upper())
        if data == None:
            return apology("must provide symbol a that is on Yahoo Stock Page. Please go to https://finance.yahoo.com/", 400)
        
        database = db.execute("SELECT * FROM Share WHERE user_id = ? AND symbol = ?;", session["user_id"],request.form.get("symbol"))

        if len(database) < 1: 

            # Redirect user to profile page of the stock
            return render_template("profile.html", placeholder=data,do='/buy')
        else:
            # Redirect user to profile page of the stock
            return render_template("profile.html", placeholder=data,do='/sell')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("company.html")


@app.route("/crypto", methods=["GET", "POST"])
@login_required
def crypto():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Calling lookup function
        data = lookup(request.form.get("symbol").upper())
        if data == None:
            return apology("must provide symbol a that is on Yahoo Stock Page. Please go to https://finance.yahoo.com/", 400)
        
        database = db.execute("SELECT * FROM Share WHERE user_id = ? AND symbol = ?;", session["user_id"],request.form.get("symbol"))
        if len(database) < 1: 

            # Redirect user to profile page of the stock
            return render_template("profile.html", placeholder=data,do='/buy')
        else:
            # Redirect user to profile page of the stock
            return render_template("profile.html", placeholder=data,do='/sell')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("crypto.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    data = db.execute("SELECT * FROM transcations WHERE User_id = ?;", session["user_id"])
    return render_template("history.html", trans_data=data)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure the symbol was submitted
        if not request.form.get("shares"):
            return apology("must provide symbol", 400)

        # Ensure the number of share is not negative was submitted
        try:
            if int(request.form.get("shares")) < 0:
                return apology("must provide a valid number that is a positive integer", 400)
        except ValueError:
            return apology("must provide a valid number that is a positive integer", 400)

        # Calling lookup function
        data = lookup(request.form.get("symbol"))

        # Selecting user money from users
        money = db.execute("SELECT cash FROM registration WHERE id = ?;", session["user_id"])
        
        # Checking if user has enough money to buy the stock
        if (data["Price"] * float(request.form.get("shares"))) > money[0]["cash"]:
            return apology("You don't have enough money", 400)

        # Buying the stock
        db.execute("UPDATE registration cash = ? WHERE id = ?;",(money[0]["cash"] - data["Price"] * float(request.form.get("shares"))),session["user_id"])
        db.execute("INSERT INTO transcations(user_id,transcation,symbol,comp_name,cost,cash,shares,date,time) VALUES(?,?,?,?,?,?,?,?,?);",
                   session["user_id"],'Buy',data["Symbol"],data["Name"],data["Price"] * float(request.form.get("shares")),
                   (money[0]["cash"] - data["Price"] * float(request.form.get("shares"))),
                   request.form.get("shares"),date.today(),now.strftime("%H:%M:%S"))
        # Chexking whether the user owns that stock before or not.
        nshare = db.execute("SELECT shares FROM Share WHERE user_id = ? AND comp_name = ? AND symbol=?;", session["user_id"], data["Name"],request.form.get("symbol"))
        if len(nshare[0]) < 1:
            db.execute("INSERT INTO Share(user_id,comp_name,shares,symbol) VALUES(?,?,?,?);",
                session["user_id"],data["Symbol"],data["Name"],request.form.get("shares"))
        else:
            share = db.execute("SELECT shares FROM Share WHERE user_id = ? AND comp_name = ? AND symbol = ?;", session["user_id"], data["Name"], request.form.get("symbol"))
            db.execute("UPDATE Share SET shares = ? WHERE user_id = ? AND symbol = ? AND comp_name = ?;",request.form.get("shares") + share[0]["shares"],
                session["user_id"],data["Symbol"],data["Name"])


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")
    

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    data = db.execute("SELECT * FROM Share WHERE user_id = ?;",session["user_id"])
    if request.method == "GET":
        return render_template("Sell.html", data=data)
    else:
        stock = lookup(request.form.get("symbol"))
        shares = int(request.form.get("shares"))
        share = db.execute("SELECT shares FROM Share WHERE user_id = ? AND comp_name = ? AND symbol = ?;", session["user_id"], stock["Name"],stock["Symbol"])
        cash = db.execute("SELECT cash FROM registration WHERE id = ?;", session["user_id"])

        # Checking if shares isn't negative or greater than the user own and also checking-
        # -that a stock is selected and stock is in the list of stocks of the seller
        if shares < 0:
            return apology("must provide a positive number", 400)

        if shares > share[0]["shares"]:
            return apology("you don't have enough shares", 400)

        # Selling the stocks
        cost = (stock["Price"] * shares)
        user_cash = cash[0]["cash"] + cost
        db.execute("UPDATE registration SET cash = ? WHERE id = ?;",user_cash,session["user_id"])
        db.execute("INSERT INTO transcations(user_id,transcation,symbol,comp_name,cost,cash,shares,date,time) VALUES(?,?,?,?,?,?,?,?,?);",
                   session["user_id"],'Sell',stock["Symbol"],stock["Name"],cost,user_cash,shares,date.today(),
                   now.strftime("%H:%M:%S"))
        # Chexking whether the user owns that stock before or not.
        db.execute("UPDATE Share SET shares = ? WHERE user_id = ? AND symbol = ? AND comp_name = ?;",share[0]["shares"] - request.form.get("shares"),
            session["user_id"],stock["Symbol"],stock["Name"])
        db.execute("DELETE FROM Share WHERE shares = 0;")

        # Redirecting back to home page
        return redirect("/")


# Register page
@app.route("/change-password", methods=["GET","POST"])
def Change_Password():
    """Showing user the register page and asking for credentials"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        confirmation = request.form.get("confirmation")
        password = request.form.get("password")
        email = request.form.get("email")
        check = db.execute("SELECT * FROM registration WHERE user_id=?;",session["user_id"])
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("please enter your user name", 400)

        # Ensuring that the username matches database
        if request.form.get("username") != check[0]["user_name"]:
            return apology("Username is incorrect", 404)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)
        
        # Ensure email was submitted
        if not email:
            return apology("must provide a password", 400)
        
        # Ensuring that the email matches database
        if email != check[0]["email_address"]:
            return apology("Email_address is incorrect", 404)

        # Confirming that confirmation is not empty
        if not confirmation:
            return apology("must provide password again", 400)

        # Confirming that confirmation is equal to password
        if confirmation != password:
            return apology("The password doesn't match", 400)

        # Adding the user to the Database
        password_hash = str(generate_password_hash(password))
        db.execute("UPDATE registration password_hash=? WHERE id=?",password_hash,session["user_id"])

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")