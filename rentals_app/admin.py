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
from rentals_app.auth import login_required, admin_only
from rentals_app.models.rental import *

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
@login_required
@admin_only
def root():
    return redirect(url_for("admin.inventory"))


# Render index page


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

        customers_ids = list()
        for x in reservations:
            customers_ids.append(x[3])

        customers = dict()
        for id in customers_ids:
            customers[str(id)] = User.find_user(id=x[3])

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


#### CRUD FUNCTIONS ####
# - CREATE
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
        rental.rate = float(request.form.get("rate"))
        rental.drive = request.form.get("drive")
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
                    rental.make, rental.model, rental.category
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


# CRUD - READ
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


# CRUD - UPDATE
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


# CRUD - DELETE
@admin.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def delete(id):
    rental = Rental().find_rental(id)
    if rental:
        shutil.rmtree("{0}_{1}_{2/}".format(rental.make, rental.model, rental.category))
    if rental.delete():
        flash("Record #" + str(id) + " successfully deleted.")
        return redirect(url_for("admin.inventory"))
    else:
        flash(
            "Something went wrong while deleting record #{}. Please contact your administrator.".format(
                id
            )
        )
        return redirect(url_for("admin.inventory"))


# Run sql from browser, if permitted by group


@admin.route("/new/fast_add", methods=["GET", "POST"])
@login_required
@admin_only
def fast_add():
    print("Executing admin sql query\n{0}".format(request.form.get("sql_query")))
    helpers.log_event(
        "[{0}] Admin executed sql from {1}\n".format(
            datetime.datetime.now(), request.remote_addr
        )
    )
    try:
        con, cur = helpers.connect_to_db()
        cur.execute(request.form.get("sql_query"))
        con.commit()
    except Exception as ex:
        con.rollback()
        flash(ex)
    finally:
        con.close()
        return redirect(url_for("admin.inventory"))


@admin.route("/schedule", methods=["GET"])
@login_required
@admin_only
def schedule():
    return render_template("admin/schedule.html")


# Add schedule_confirm route
# Update rental to not available
# Update rented_by
# Update available_on
# Add appt to calendar
# Message user