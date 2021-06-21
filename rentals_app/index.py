from flask import Blueprint
from flask import (
    url_for,
    redirect,
    render_template,
    request,
    flash,
)
from rentals_app.models.rental import Rental
import rentals_app.helpers as helpers


index = Blueprint("index", __name__, url_prefix="/")


@index.route("/")
def root():
    con, cur = helpers.connect_to_db()
    ids = cur.execute("SELECT id FROM INVENTORY").fetchall()
    rentals = []
    for id_list in ids:
        for id in id_list:
            rentals.append(Rental().find_rental(id))
    for rental in rentals:
        rental.rate = float(rental.rate[0])
        rental.image_paths = list(
            rental.image_paths.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
        )
        rental.implements = list(
            rental.implements.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
        )

    return render_template("index.html", rentals=rentals)


@index.route("/root/")
def application_root():
    return redirect(url_for("index.index"))


@index.route("/contact")
def contact():
    return render_template("contact.html")


@index.route("/contact/send", methods=["POST"])
def contact_send():
    if request.method == "POST":
        data = {
            "name": "%s %s" % (request.form.get("f_name"), request.form.get("l_name")),
            "phone": request.form.get("p_number"),
            "email": request.form.get("email"),
            "subject": request.form.get("subject"),
            "body": request.form.get("body"),
        }

        msg_body = """
        <!doctype html>
        <html>
        <head></head>
        <body>
            <h3><u>New contact request from Red Dirt Rentals</u></h3>
            <p>Name: {0}</p>
            <p>Phone Number: {1}</p>
            <p>Email: {2}</p>
            <h4>-- Message Follows --</h4>
            <p><b>{3}</b></p>
            <p>{4}</p>
        </body>
        </html>
        """.format(
            data["name"], data["phone"], data["email"], data["subject"], data["body"]
        )

        try:
            helpers.send_mail(["admin@reddirtequipment.com"], msg_body, data["subject"])
            flash("Message sent, thanks for contacting us. We'll get back to you in 3-5 business days.")
            return redirect(url_for('index.contact'))
        except Exception as ex:
            raise ex


@index.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@index.route('/terms-of-service')
def terms():
    return render_template('terms.html')