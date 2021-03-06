from datetime import datetime

from flask import (
    Blueprint,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import rentals_app.helpers as helpers
from rentals_app.auth import login_required
from rentals_app.models.rental import Rental
from rentals_app.models.user import User
from rentals_app.models.message import Message

account = Blueprint("account", __name__, url_prefix="/account")


@account.route("/")
@login_required
def index():
    return render_template("account/index.html", user=g.user)


@account.route("/reservations")
@login_required
def reservations():
    con, cur = helpers.connect_to_db()
    resv_sql = "SELECT * FROM reservations WHERE customer_id = '{}';".format(
        g.user.userid
    )
    try:
        reservations = cur.execute(resv_sql).fetchall()

        rental_ids = list()
        for x in reservations:
            rental_ids.append(x[2])

        rentals = dict()
        for id in rental_ids:
            rentals[str(id)] = Rental().find_rental(id)
            rentals[str(id)].image_paths = rentals[str(id)].image_paths[
                2 : len(rentals[str(id)].image_paths) - 2
            ]

        return render_template(
            "account/reservations.html", reservations=reservations, rentals=rentals
        )
    except Exception as ex:
        print(ex)
        raise ex
    finally:
        con.close()


@account.route("/reserve/<int:id>")
@login_required
def reserve(id):
    return render_template("account/reserve.html", id=id)


@account.route("/reserve/<int:r_id>/", methods=["POST"])
@login_required
def make_reservation(r_id):
    if r_id is not None and r_id >= 0:
        if g.user is not None:

            data = {
                "start_1": request.form.get("start_1"),
                "start_2": request.form.get("start_2"),
                "start_3": request.form.get("start_3"),
                "end_1": request.form.get("end_1"),
                "end_2": request.form.get("end_2"),
                "end_3": request.form.get("end_3"),
                "hours": request.form.get("usage_hours"),
            }
            day = datetime.today()
            conf_no = "{0}{1}{2}-{3}-{4}".format(
                day.year, day.month, day.day, r_id, g.user.userid
            )

            con, cur = helpers.connect_to_db()
            sql = """
            INSERT INTO reservations (
                confirmation_num,
                rental_id,
                customer_id,
                pref_start_1,
                pref_start_2,
                pref_start_3,
                pref_end_1,
                pref_end_2,
                pref_end_3,
                est_hours
            )
            VALUES (
                '{0}',
                '{1}',
                '{2}',
                '{3}',
                '{4}',
                '{5}',
                '{6}',
                '{7}',
                '{8}',
                '{9}'
            );
            """.format(
                conf_no,
                r_id,
                g.user.userid,
                data["start_1"],
                data["start_2"],
                data["start_3"],
                data["end_1"],
                data["end_2"],
                data["end_3"],
                data["hours"],
            )
            try:
                cur.execute(sql)
                con.commit()
                return redirect(url_for("account.reserve_confirm", conf_no=conf_no))
            except Exception as ex:
                con.rollback()
                raise ex
    else:
        flash("Please select a rental first.")
        return redirect(url_for("account.reserve", conf_no=None))


@account.route("/reserve/confirm/<conf_no>")
@login_required
def reserve_confirm(conf_no):
    if conf_no:
        return render_template("account/confirm_reservation.html", conf_no=conf_no)


@account.route("/reserve/cancel-reservation/<conf_no>", methods=["POST"])
@login_required
def cancel_reservation(conf_no):
    if request.method == "POST":
        con, cur = helpers.connect_to_db()

        try:
            # Update reservation status
            SQL = """
            UPDATE reservations 
            SET 
                status='CANCELED BY CUSTOMER',
                customer_id='0'
            WHERE confirmation_num='{}';
            """.format(
                conf_no
            )

            cur.execute(SQL)
            con.commit()

            # Change rental attributes
            SQL = """
            SELECT rental_id FROM reservations WHERE confirmation_num='{}';
            """.format(
                conf_no
            )

            id = con.execute(SQL).fetchone()
            rental = Rental().find_rental(id[0])

            # Update Rental
            updated_rental = rental.clone(rental)
            updated_rental.is_available = 1
            updated_rental.rented_by = None
            updated_rental.is_shown = 1
            rental.available_on = None
            Rental.update(updated_rental, updated_rental.rental_id)

            body = """
            <!doctype html>
            <html>
            <head></head>
            <body>
                <h3>Your reservation has been successfully cancelled.</h3>
                <p><b>Confirmation Number: {0}</b></p>
                <p>
                    To view your messages, reply and see status updates, sign in to your account
                    at <a href="rentals.reddirtequipment.com/account/">Red Dirt Rentals</a>
                </p>
                <br>
                <br>
                <p>Best Regards,</p>
                <p>Red Dirt Rentals</p>
            </body>
            </html>            
            """.format(
                conf_no
            )
            helpers.send_mail(
                to=[g.user.email],
                body=body,
                subject="You have canceled your reservation at Red Dirt Rentals.",
            )

            flash("Successfully cancelled reservation.")
            return redirect(url_for("account.reservations"))

        except Exception as ex:
            print(ex)
            con.rollback()
            raise ex

        finally:
            con.close()


@account.route("/messages")
@login_required
def render_messages():
    messages = Message.get_messages(User.find_user(g.user.userid))
    users_friendly = dict()
    for msg in messages:
        users_friendly[msg[1]] = User.find_user(msg[1]).firstname

    emails = list()
    if g.user.groups == "admin":
        users = User.get_all_users()
        for user in users:
            emails.append(user[4])
        return render_template(
            "account/messages.html",
            messages=messages,
            users_friendly=users_friendly,
            emails=emails,
        )

    return render_template(
        "account/messages.html", messages=messages, users_friendly=users_friendly
    )


@account.route("/messages/send", methods=["POST"])
@login_required
def send_message():
    if request.method == "POST":
        if g.user.groups != "admin":
            msg_to = 2
        else:
            msg_to = User.find_user_by_email(request.form.get("msg_to")).userid
            msg_from = g.user.userid
            msg_subject = request.form.get("msg_subject")
            msg_body = request.form.get("msg_body")

        msg = Message(
            from_user=msg_from, to_user=msg_to, subject=msg_subject, message=msg_body
        )
        msg.send_message()
        flash("Message Sent!")
        return redirect(url_for("account.render_messages"))


@account.route("/update-information", methods=["POST"])
def update_info():
    if request.method == "POST":
        form = {
            "f_name": request.form.get("f_name"),
            "l_name": request.form.get("l_name"),
            "email": request.form.get("email"),
            "phonenumber": request.form.get("phonenumber"),
            "address": request.form.get("address"),
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "zip": request.form.get("zip"),
        }

        con, cur = helpers.connect_to_db()
        SQL = """
        UPDATE users SET
            firstname="{0}",
            lastname="{1}",
            email="{2}",
            phonenumber="{3}",
            address="{4}",
            city="{5}",
            state="{6}",
            zip="{7}"
        WHERE id={8};
        """.format(
            form["f_name"],
            form["l_name"],
            form["email"],
            form["phonenumber"],
            form["address"],
            form["city"],
            form["state"],
            form["zip"],
            g.user.userid,
        )
        try:
            cur.execute(SQL)
            con.commit()
            flash("Your information has been successfully updated.")
            return redirect(url_for('account.index'))
        except Exception as ex:
            raise ex
        finally:
            con.close()

