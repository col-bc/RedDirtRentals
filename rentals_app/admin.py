import datetime
import os
import shutil

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    g,
)

import rentals_app.helpers as helpers
from rentals_app.models.user import *
from rentals_app.models.message import Message
from rentals_app.auth import login_required, admin_only
from rentals_app.models.rental import *

admin = Blueprint("admin", __name__, url_prefix="/admin")

# Root route for blueprint
@admin.route("/")
@login_required
@admin_only
def root():
    return redirect(url_for("admin.inventory"))


# Render Rental Index page
@admin.route("/inventory")
@login_required
@admin_only
def inventory():
    con, cur = helpers.connect_to_db()
    ids = list(cur.execute("SELECT id FROM inventory;").fetchall())
    rentals = []
    for id_list in ids:
        for id in id_list:
            rentals.append(Rental().find_rental(id))
    for rental in rentals:
        rental.implements = list(
            rental.implements.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
        )
        rental.image_paths = list(
            rental.image_paths.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
        )

    reservations = list(cur.execute("SELECT * FROM reservations;").fetchall())
    con.close()

    return render_template(
        "admin/index.html", rentals=rentals, reservations=reservations
    )


# Render New page
@admin.route("/new")
@login_required
@admin_only
def new():
    return render_template("admin/new.html")


# Render Reservations Page
@admin.route("/reservations")
@login_required
@admin_only
def reservations():
    con, cur = helpers.connect_to_db()
    resv_sql = "SELECT * FROM reservations;".format(g.user.userid)
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

        print(reservations)
        customers_ids = list()
        for x in reservations:
            customers_ids.append(x[3])

        customers = dict()
        for id in customers_ids:
            if id == 0:
                customers[str(id)] = None
            else:
                customers[str(id)] = User.find_user(id)

    except Exception as ex:
        print(ex)
        raise ex

    finally:
        con.close()
        return render_template(
            "admin/reservations.html",
            reservations=reservations,
            rentals=rentals,
            customers=customers,
        )


# Render Detailed Rental Pages
@admin.route("/reservations/<int:id>", methods=["GET"])
@login_required
@admin_only
def reservation_details(id):
    SQL = """SELECT * FROM reservations WHERE id={}""".format(id)
    con, cur = helpers.connect_to_db()
    try:
        reservation = cur.execute(SQL).fetchone()
    except Exception as ex:
        print(ex)
        raise ex
    print(reservation, type(reservation))
    customer = User.find_user(reservation[3])
    rental = Rental().find_rental(reservation[2])
    image = rental.image_paths.strip("[").strip("]").strip("'")
    return render_template(
        "admin/reservation_detail.html",
        reservation=reservation,
        customer=customer,
        rental=rental,
        image=image,
    )


# Update Rental status
@admin.route("/reservations/update-status/<int:id>", methods=["POST"])
@login_required
@admin_only
def update_resv_status(id):
    if request.method == "POST":
        status = request.form.get("new_status")
        con, cur = helpers.connect_to_db()
        SQL = """
        UPDATE reservations SET status="{0}" WHERE id={1}
        """.format(
            status, id
        )

        try:
            cur.execute(SQL)
            con.commit()
            return redirect(url_for("admin.reservation_details", id=id))
        except Exception as ex:
            con.rollback()
            print(ex)
            raise (ex)
        finally:
            con.close()


# Render customer
@admin.route("/customers")
@login_required
@admin_only
def customers():
    cur, con = helpers.connect_to_db()
    sql = """
    SELECT id FROM users WHERE 1=1;
    """
    try:
        ids = cur.execute(sql).fetchall()
        customers = list()
        for id in ids:
            customers.append(User.find_user(id[0]))
    except Exception as ex:
        current_app.log_exception(ex)
        raise ex

    return render_template("admin/customers.html", customers=customers)


#### INVENTORY CRUD FUNCTIONS ####
# CREATE
@admin.route("/new/create/", methods=["POST", "GET"])
@login_required
@admin_only
def create():
    rental = Rental()
    if request.method == "POST":

        rental.category = request.form.get("category")
        rental.make = request.form.get("make")
        rental.model = request.form.get("model")
        rental.fuel_type = request.form.get("fuel_type")
        rental.horse_power = request.form.get("horse_power")
        rental.deck_size = request.form.get("deck_size")
        rental.implements = request.form.getlist("implements")
        rental.stock = request.form.get("stock")
        rental.drive = request.form.get("drive")
        rental.rate = float(request.form.get("rate"))
        rental.job_category = request.form.get("job_category")
        rental.price_range = request.form.get("price_range")
        rental.is_available = 1 if request.form.get("is_available") == "Yes" else 0
        rental.available_on = datetime.datetime.strptime(
            request.form.get("available_on"), "%Y-%m-%d"
        ).date()
        rental.rented_by = request.form.get("rented_by")
        rental.rent_queue = request.form.get("rent_queue")
        rental.is_shown = 1 if request.form.get("is_shown") == "Yes" else 0
        rental.description = request.form.get("description")
        rental.features = request.form.get("features")

        paths = []
        files = request.files.getlist("files")
        for file in files:
            if file:
                folder_format = "/{0}_{1}_{2}/".format(
                    rental.make.strip(" "),
                    rental.model.strip(" "),
                    rental.category.strip(" "),
                )
                if not os.path.exists(helpers.ABS_UPLOAD_PATH + folder_format):
                    os.mkdir(helpers.ABS_UPLOAD_PATH + folder_format)
                filename = secure_filename(file.filename)
                file.save(helpers.ABS_UPLOAD_PATH + folder_format + filename)
                paths.append(
                    os.path.join(current_app.static_url_path, folder_format + filename)
                )
        rental.image_paths = paths

        if rental.insert():
            return redirect(url_for("admin.inventory"))
        else:
            flash("Could not add rental. Please try again.")
            return redirect(url_for("admin.inventory"))


@admin.route("/new/create/add-photo", methods=["POST"])
@login_required
@admin_only
def add_photo():
    if request.method == "POST":
        pass


# READ
@admin.route("/details/<int:id>")
@login_required
@admin_only
def details(id):
    rental = Rental().find_rental(rental_id=id)
    rental.image_paths = list(
        rental.image_paths.replace("[", "").replace("]", "").replace("'", "").split(",")
    )
    rental.implements = list(
        rental.implements.replace("[", "").replace("]", "").replace("'", "").split(",")
    )
    return render_template("admin/details.html", rental=rental)


# UPDATE
@admin.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def update(id):
    rental = Rental()
    print("Shown is: " + request.form.get("is_available"))
    if request.method == "POST":
        rental.category = request.form.get("category")
        rental.make = request.form.get("make")
        rental.model = request.form.get("model")
        rental.fuel_type = request.form.get("fuel_type")
        rental.horse_power = request.form.get("horse_power")
        rental.deck_size = request.form.get("deck_size")
        rental.implements = request.form.getlist("implements")
        rental.stock = request.form.get("stock")
        rental.rate = float(request.form.get("rate"))
        rental.drive = request.form.get("drive")
        rental.job_category = request.form.get("job_category")
        rental.price_range = request.form.get("price_range")
        rental.is_available = 1 if request.form.get("is_available") == "on" else 0
        rental.available_on = datetime.datetime.strptime(
            request.form.get("available_on"), "%Y-%m-%d"
        ).date()
        rental.rented_by = request.form.get("rented_by")
        rental.rent_queue = request.form.get("rent_queue")
        rental.is_shown = 1 if request.form.get("is_shown") == "on" else 0
        rental.description = request.form.get("description")
        rental.features = request.form.get("features")

        files = request.files.getlist("files")
        if files[0].filename is None or files[0].filename == "":
            paths = Rental().find_rental(id).image_paths

        else:
            paths = []
            for file in files:
                if file:
                    folder_format = "/{0}_{1}_{2}/".format(
                        rental.make, rental.model, rental.category
                    )
                    if not os.path.exists(helpers.ABS_UPLOAD_PATH + folder_format):
                        os.mkdir(helpers.ABS_UPLOAD_PATH + folder_format)

                    filename = secure_filename(file.filename)
                    file.save(helpers.ABS_UPLOAD_PATH + folder_format + "/" + filename)
                    paths.append(
                        os.path.join(
                            current_app.static_url_path, folder_format + filename
                        )
                    )
        rental.image_paths = paths

        if Rental.update(rental, id):
            flash("Record was successfully updated")
            return redirect(url_for("admin.details", id=id))
        else:
            flash("Something went wrong while updating this record. Please try again.")
            return redirect(url_for("admin.details", id=id))


# DELETE
@admin.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def delete(id):
    rental = Rental().find_rental(id)
    if rental:
        try:
            shutil.rmtree(
                "{0}_{1}_{2}".format(rental.make, rental.model, rental.category)
            )
        except FileNotFoundError or IOError:
            pass
    if rental.delete():
        flash("Record #" + str(id) + " successfully deleted.")
        return redirect(url_for("admin.inventory"))
    else:
        flash(
            "Something went wrong while deleting record #{}. Please contact your webmaster.".format(
                id
            )
        )
        return redirect(url_for("admin.inventory"))


# Render schedule
@admin.route("/schedule", methods=["GET"])
@login_required
@admin_only
def schedule():
    con, cur = helpers.connect_to_db()
    SQL = """
    SELECT * FROM reservations 
    WHERE 
        actual_start IS NOT NULL 
    AND 
        actual_end IS NOT NULL
    AND status IS NOT 'DELETED ACCOUNT';"""
    try:
        reservations = cur.execute(SQL).fetchall()
        con.close()
    except Exception as ex:
        print(ex)
        raise ex

    class Event:
        def __init__(
            self, start_date, end_date, customer, reservation_id, status
        ) -> None:
            self.start_date = start_date
            self.end_date = end_date
            self.customer = customer
            self.reservation_id = reservation_id
            self.status = status

    events = list()
    for x in reservations:
        print(x)
        events.append(
            Event(
                start_date=x[12],
                end_date=x[13],
                customer=x[3],
                reservation_id=x[0],
                status=x[10],
            )
        )

    return render_template("admin/schedule.html", events=events)


@admin.route("/schedule/confirm/<int:r_id>/<int:c_id>/<int:rsvr_id>", methods=["POST"])
@login_required
@admin_only
def schedule_confirm(r_id, c_id, rsvr_id):
    if request.method == "POST":
        # Update Rental
        rental = Rental().find_rental(r_id)
        user = User.find_user(c_id)
        updated_rental = rental.clone(rental)
        updated_rental.is_available = 0
        updated_rental.rented_by = "%s %s" % (user.firstname, user.lastname)
        updated_rental.is_shown = 0
        rental.available_on = request.form.get("scheduled_end")
        Rental.update(updated_rental, updated_rental.rental_id)

        body = """
            <!doctype html>
            <html>
            <head></head>
            <body>
                <h3>Your reservation has been confirmed by Red Dirt Rentals</h3>
                <p><b>Your rental is scheduled for {0} to {1}</b></p>
                <p>
                    To view your messages, reply and see status updates, sign in to your account
                    at <a href="rentals.reddirtequipment.com/account/">Red Dirt Rentals</a>
                </p>
            </body>
            </html>            
        """.format(
            request.form.get("scheduled_start"), request.form.get("scheduled_end")
        )
        helpers.send_mail(
            to=user.email, body=body, subject="You have an update from Red Dirt Rentals"
        )

        con, cur = helpers.connect_to_db()
        SQL = """
        UPDATE reservations 
        SET 
            actual_start="{0}", 
            actual_end="{1}"
        WHERE id={2}
        """.format(
            request.form.get("scheduled_start"),
            request.form.get("scheduled_end"),
            rsvr_id,
        )
        try:
            cur.execute(SQL)
            con.commit()
            return redirect(url_for("admin.reservations", id=rsvr_id))
        except Exception as ex:
            print(ex)
            con.rollback()
            raise ex
        finally:
            con.close()
