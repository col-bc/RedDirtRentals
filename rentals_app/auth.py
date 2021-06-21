import functools
from datetime import timedelta, datetime
from logging import exception
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
)
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
        print(ex)
        return redirect(url_for("auth.login"))

    if db is not None and db[1] == username and check_password_hash(db[2], password):
        session["userid"] = db[0]
        return redirect(url_for("account.index"))

    con.close()
    flash("Username or password does not match our records")
    return redirect(url_for("auth.login"))


@auth.route("/register")
def register():
    return render_template("auth/register.html", user=User())


@auth.route("/register/enroll", methods=["GET", "POST"])
def enroll():
    if request.method == "POST":
        if not helpers.password_check(request.form.get("password"))["password_ok"]:
            flash("Password does not meet complexity requirements. Try again.")
            return redirect(url_for("auth.register"))
        user = User(
            firstname=request.form.get("firstname"),
            lastname=request.form.get("lastname"),
            phonenumber=request.form.get("phonenumber"),
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password")),
            groups="Customer",
            address="{0} {1}".format(
                request.form.get("address1"),
                request.form.get("address2")
                if request.form.get("address2") is not None
                else "",
            ),
            city=request.form.get("city"),
            state=request.form.get("state"),
            zip=request.form.get("zip"),
        )

        cur, con = helpers.connect_to_db()
        sql = "SELECT * FROM users WHERE email='{}'".format(request.form.get("email"))

        try:
            db = cur.execute(sql).fetchone()
        except Exception as ex:
            print(ex)
            raise ex
        finally:
            con.close()

        if db is not None:
            flash("There is already an account registered with this email.")
            return redirect(url_for("auth.register"))
        else:
            try:
                user.create_user()
                flash("Your account has been created, please login now.")
                return redirect(url_for("auth.login"))
            except Exception as ex:
                print(ex)
                flash(
                    "We cannot create this account right now. Please try again in a little while."
                )
                return redirect(url_for("auth.register"))


# Service
# TODO: fix password_check compliance bug
@auth.route("/change-password", methods=["GET", "POST"])
def change_password():
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


@auth.route("/reset-password")
def reset_password():
    return render_template("auth/reset.html")


#TODO: handle email send asynchronously 
@auth.route("/reset-password/request", methods=["POST"])
def reset_request():
    email = request.form.get("email")

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
                print(SQL)
                cur.execute(SQL)
                con.commit()

                body = """
                    <!doctype html>
                    <html>
                    <head></head>
                    <body>
                        <h3>Someone has requested a password reset for your account at Red Dirt Rentals</h3>
                        <p>If this was not you, please disregard this email. A reset will not occur unless you click the link below</p>
                        <p>To reset your password, please click the link below.</p>
                        {}
                    </body>
                    </html>
                """.format(
                    token
                )
                helpers.send_mail(
                    to=["colby.b.cooper@gmail.com"],
                    subject="Here's your password reset from Red Dirt Rentals",
                    body=body,
                )
            except Exception as ex:
                raise ex

    # Doesn't work because threat is out of application context
    thread = threading.Thread(
        target=handle_reset_request, kwargs={"email": email}
    )
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
            print(SQL)
            cur.execute(SQL)
            con.commit()

            body = """
                <!doctype html>
                <html>
                <head></head>
                <body>
                    <h3>Someone has requested a password reset for your account at Red Dirt Rentals</h3>
                    <p>If this was not you, please disregard this email. A reset will not occur unless you click the link below</p>
                    <p>To reset your password, please click the link below.</p>
                    {}
                </body>
                </html>
            """.format(
                token
            )
            helpers.send_mail(
                to=["colby.b.cooper@gmail.com"],
                subject="Here's your password reset from Red Dirt Rentals",
                body=body,
            )
        except Exception as ex:
            raise ex
    return


@auth.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    if request.method == "POST":
        user = User.find_user(g.user.userid)
        print(g.user.email)
        print(request.form.get("del_username"))
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


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
