from flask import redirect, render_template, request, session
from functools import wraps

import yfinance as yf


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    ticker = yf.Ticker(symbol).info
    return {
        'Name' : ticker['longName'],
        'Price' : ticker['regularMarketPrice'],
        'Symbol' : ticker['symbol']
        }


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
