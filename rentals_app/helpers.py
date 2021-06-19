import sqlite3
from flask import current_app
import re
from flask_mail import Mail, Message

ABS_UPLOAD_PATH = "/Users/colby/Work/RedDirtRentals/rentals_app/static/uploads"
DB_PATH = "/Users/colby/Work/RedDirtRentals/database.db"
ALLOWED_EXTENSIONS = {"png", "jpg", "tiff", "jpeg"}


def connect_to_db():
    con = sqlite3.connect(DB_PATH)
    return con, con.cursor()

def log_event(msg):
    with open("/Users/colby/Work/RedDirtRentals/events.log", "a+") as log:
        log.write(msg)
        log.close()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def password_check(password):
    """
    Password Policy:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    length_error = len(password) < 8
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
    password_ok = not (
        length_error
        or digit_error
        or uppercase_error
        or lowercase_error
        or symbol_error
    )
    return {
        "password_ok": password_ok,
        "length_error": length_error,
        "digit_error": digit_error,
        "uppercase_error": uppercase_error,
        "lowercase_error": lowercase_error,
        "symbol_error": symbol_error,
    }


def send_mail():
    from rentals_app import app
    mail = Mail(app)

    app.MAIL_SERVER = "smtp.office365.com"
    app.MAIL_PORT = "587"
    app.MAIL_USERNAME = "ccooper@reddirtequipment.com"
    app.MAIL_PASSWORD = "Av3ryJ4x!0711#"
    app.MAIL_USE_TLS = True

    body = """
    <!doctype HTML>
    <head></head>
    <body>
        <h1>You have a new message from Red Dirt Rentals!</h1>
        <p>To read your messages, click the link below.</p>
        <a href="localhost:5000/auth/login/">Read Messages</a>
    </body>
    """
    msg = Message(html=body,
                    subject="New Message From Red Dirt Rentals",
                  sender="admin@reddirtequipment.com.com",
                  recipients=["colby.b.cooper@gmail.com"])
    mail.send(msg)