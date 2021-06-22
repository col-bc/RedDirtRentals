import functools
from datetime import timedelta, datetime
import uuid
import threading

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
from flask.app import Flask
from werkzeug.security import check_password_hash, generate_password_hash

import rentals_app.helpers as helpers
from rentals_app.models.user import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.before_app_request
def fetch_current_user():
    userid = session.get("userid")
    if userid is None:
        g.user = None
    else:
        g.user = User.find_user(userid)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def admin_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        if g.user is not None and g.user.groups != "admin":
            session.clear()
            return redirect(render_template("errors/401.html"))

        return view(**kwargs)

    return wrapped_view


# Routes


@auth.route("/")
def root():
    return redirect("login")


# -Login-
@auth.route("/login")
def login():
    return render_template("auth/login.html")


@auth.route("/login/verify", methods=["GET", "POST"])
def verify():
    username = str(request.form.get("email")).lower()
    password = request.form.get("password")

    cur, con = helpers.connect_to_db()
    sql = "SELECT id,email,password FROM users WHERE email='{}'".format(username)

    try:
        db = cur.execute(sql).fetchone()
    except Exception as ex:
        flash("Username or password does not match our records.")
        (ex)
        return redirect(url_for("auth.login"))

    if db is not None and db[1] == username and check_password_hash(db[2], password):
        session["userid"] = db[0]
        return redirect(url_for("account.index"))

    con.close()
    flash("Username or password does not match our records")
    return redirect(url_for("auth.login"))


# -Register-
@auth.route("/register")
def register():
    return render_template("auth/register.html", user=User())


@auth.route("/register/enroll", methods=["GET", "POST"])
def enroll():
    if request.method == "POST":
        # Check password strength
        if not helpers.password_check(request.form.get("password"))["password_ok"]:
            flash("Password does not meet complexity requirements. Try again.")
            return redirect(url_for("auth.register"))
        # Create user obj
        user = User(
            firstname=request.form.get("firstname"),
            lastname=request.form.get("lastname"),
            phonenumber=request.form.get("phonenumber"),
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password")),
            groups="Customer",
            address=request.form.get("address"),
            city=request.form.get("city"),
            state=request.form.get("state"),
            zip=request.form.get("zip"),
        )

        cur, con = helpers.connect_to_db()
        sql = "SELECT * FROM users WHERE email='{}'".format(request.form.get("email"))

        try:
            db = cur.execute(sql).fetchone()
        except Exception as ex:
            raise ex
        finally:
            con.close()

        # Check for existing account
        if db is not None:
            flash("There is already an account registered with this email.")
            return redirect(url_for("auth.register"))
        else:
            try:
                # Create User
                user.create_user()
                flash("Your account has been created, please login now.")
                return redirect(url_for("auth.login"))
            except Exception as ex:
                (ex)
                flash(
                    "We cannot create this account right now. Please try again in a little while."
                )
                return redirect(url_for("auth.register"))
            finally:
                con.close()


# -Password Utilities-
@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    ### Changes the password of a logged in user who knows their current account password. ###
    if request.method == "POST":
        user = User.find_user(g.user.userid)
        if check_password_hash(user.password, request.form.get("current_password")):
            if request.form.get("password1") == request.form.get("password2"):
                if helpers.password_check(request.form.get("password2"))["password_ok"]:
                    updated_user = user.clone()

                    updated_user.password = generate_password_hash(
                        request.form.get("password2")
                    )
                    User.update_user(updated_user.userid, updated_user)

                    flash("Your password has been changed. Please login again.")
                    return redirect(url_for("auth.logout"))
                else:
                    flash("Password does not meet complexity requirements. Try again.")
                    return redirect(url_for("account.index"))
            else:
                flash("New passwords did not match. Try again.")
                return redirect(url_for("account.index"))
        else:
            flash("Your current password was incorrect. Try again")
            return redirect(url_for("account.index"))


@auth.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    if request.method == "POST":
        user = User.find_user(g.user.userid)
        (g.user.email)
        (request.form.get("del_username"))
        if request.form.get("del_username") == g.user.email and check_password_hash(
            g.user.password, request.form.get("del_password")
        ):
            if user.firstname == "admin":
                flash(
                    "There was a problem deleting your account.\
                        You cannot delete this account because you are a site administrator."
                )
                return redirect(url_for("account.index"))
            if user.delete_user():
                flash("Your account has been deleted. We'll miss you.")
                session.clear()
                return redirect(url_for("auth.login"))
            else:
                flash(
                    "There was a problem deleting your account. Please call us for assistance."
                )
                return redirect(url_for("account.index"))
        else:
            flash(
                "There was a problem deleting your account. Your username or password was incorrect."
            )
            return redirect(url_for("account.index"))


@auth.route("/reset-password")
def reset_password():
    return render_template("auth/reset.html")


@auth.route("/reset-password/request", methods=["POST"])
def reset_request():
    """Attempts to generate token for provided email after verifying user exists."""
    email = request.form.get("email")

    thread = threading.Thread(target=handle_reset_request, kwargs={"email": email})
    thread.start()

    return render_template("auth/reset_confirm.html")


def handle_reset_request(email):
    con, cur = helpers.connect_to_db()
    user = User.find_user_by_email(email)
    if user:
        try:
            token = uuid.uuid4().hex
            expire = datetime.now() + timedelta(hours=1)
            SQL = """
                INSERT INTO resets (
                    token,
                    token_expiration,
                    userid,
                    used
                )
                VALUES (
                    "{0}",
                    "{1}",
                    "{2}",
                    "{3}"
                );
            """.format(
                token, expire, user.userid, 0
            )
            (SQL)
            cur.execute(SQL)
            con.commit()
            send_reset_email(token, email)
        except Exception as ex:
            raise ex
    return


def send_reset_email(token, email):
    body = """
        <!doctype html>
        <html>
        <head></head>
        <body style="font-family: Roboto, Arial, Helvetica, sans-serif">
            <h1>Red Dirt Rentals</h1>
            <h5>Someone has requested a password reset for your account at Red Dirt Rentals</h5>
            <hr>
            <p>If this was not you, please disregard this email. Nothing will happen to your account if you do not proceed with the reset.</p>
            <p>To reset your password, please click the link below.</p>
            <a href="localhost:5000/auth/reset/{}">Reset my password</a>
        </body>
        </html>
        """.format(
        token
    )
    helpers.send_mail(
        to=[email],
        subject="Red Dirt Rentals Password Reset",
        body=body,
    )


@auth.route("/reset/<token>", methods=["GET"])
def reset_token_validate(token):
    con, cur = helpers.connect_to_db()
    SQL = """
    SELECT * FROM resets WHERE token="{}";
    """.format(
        token
    )

    # Try to match token 
    try:
        result = cur.execute(SQL).fetchone()
    except Exception as ex:
        raise ex
    if result:
        data = {
            "token": result[1],
            "expiration": result[2],
            "userid": result[3],
            "used": result[4],
        }
        #2021-06-21 00:10:55.230429
        # Check if token is expired
        if datetime.strptime(data["expiration"], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            # Check if token has been used:
            if data["used"] == 0:
                user = User.find_user(data["userid"])
                SQL = """ 
                UPDATE resets SET used=1 WHERE token="{}";
                """.format(
                    data["token"]
                )
                try:
                    cur.execute(SQL)
                    con.close()
                    return render_template("auth/new_password.html", user=user)
                except Exception as ex:
                    raise ex
    flash('The provided token was not valid. Please request a new reset email.')
    return redirect(url_for('auth.login'))


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
