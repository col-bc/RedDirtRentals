import functools
from datetime import timedelta

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
        if not helpers.password_check(request.form.get("password")):
            flash("Password does not meet complexity requirements")
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
@auth.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        user = User.find_user(g.user.userid)
        if check_password_hash(user.password, request.form.get("current_password")):
            if request.form.get("password1") == request.form.get("password2"):
                if helpers.password_check(request.form.get("password2")):
                    updated_user = user.clone()

                    updated_user.password = generate_password_hash(
                        request.form.get("password2")
                    )
                    User.update_user(updated_user.userid, updated_user)

                    flash("Your password has been changed. Please login again.")
                    return redirect(url_for("auth.logout"))
                else:
                    flash("Password does not meet complexity requirements.")
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


@auth.route("/reset-password/request", methods=["POST"])
def reset_request():
    g.email = request.form.get("email")
    # Run async to prevent account enumeration
    # asyncio.run(main())
    return render_template("auth/reset_confirm.html")


@auth.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    if request.method == "POST":
        user = User.find_user(g.user.userid)
        print(g.user.email)
        print(request.form.get('del_username'))
        if request.form.get("del_username") == g.user.email and check_password_hash(
            g.user.password, request.form.get('del_password')
        ):
            if user.firstname == "admin":
                flash(
                    "You cannot delete this account. Please contact your administrator."
                )
                return redirect(url_for("account.index"))
            if user.delete_user():
                flash("Your account has been deleted. We'll miss you.")
                session.clear()
                return redirect(url_for("auth.login"))
            else:
                flash(
                    "There as a problem processing your request. Please call us for assistance."
                )
                return redirect(url_for("account.index"))
        else:
            flash("You username or password was incorrect.")
            return redirect(url_for("account.index"))


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response
