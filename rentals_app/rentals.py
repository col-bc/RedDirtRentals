from flask import (
    url_for,
    redirect,
    Blueprint,
    render_template,
    jsonify,
    Response,
    abort,
    flash,
)
from rentals_app.models.rental import Rental
import rentals_app.helpers as helpers

rentals = Blueprint("Rentals", __name__, url_prefix="/rentals")


@rentals.route("/")
def root():
    return redirect(url_for("Rentals.all_rentals"))


@rentals.route("/all")
def all_rentals():
    con, cur = helpers.connect_to_db()
    ids = cur.execute("SELECT id FROM inventory WHERE is_shown == 1").fetchall()
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

    return render_template("rentals/index.html", rentals=rentals)


@rentals.route("/details/<int:id>", methods=["GET"])
def details(id):
    con, cur = helpers.connect_to_db()
    fetched_id = cur.execute(
        "SELECT id FROM inventory WHERE id='{}';".format(id)
    ).fetchone()
    rental = Rental().find_rental(fetched_id[0])

    rental.rate = float(rental.rate[0])
    rental.image_paths = list(
        rental.image_paths.replace("[", "").replace("]", "").replace("'", "").split(",")
    )
    rental.implements = list(
        rental.implements.replace("[", "").replace("]", "").replace("'", "").split(",")
    )
    print(rental)

    return render_template("rentals/details.html", rental=rental)


@rentals.route("/get-rental/<int:id>", methods=["GET"])
def get_rental(id):
    rental = Rental().find_rental(id)
    if not rental:
        return abort(500)

    rental.rate = float(rental.rate[0])
    rental.image_paths = list(
        rental.image_paths.replace("[", "").replace("]", "").replace("'", "").split(",")
    )
    rental.implements = list(
        rental.implements.replace("[", "").replace("]", "").replace("'", "").split(",")
    )

    return Response(jsonify(rental), 200)


@rentals.route("/filter/<category>/<critera>", methods=["GET"])
def filter(category, critera):
    con, cur = helpers.connect_to_db()
    if category == "Type":
        SQL = "SELECT * FROM inventory WHERE category='{}';".format(critera)
    elif category == "Price":
        SQL = "SELECT * FROM inventory WHERE rate < {};".format(critera)
    elif category == "Job":
        SQL = "SELECT * FROM inventory WHERE job_category='{}';".format(critera)

    try:
        results = cur.execute(SQL).fetchall()
        if results:
            filtered_rentals = list()
            for rental in results:
                filtered_rentals.append(Rental().find_rental(rental[0]))

                for rental in filtered_rentals:
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

            return render_template("rentals/index.html", filtered=filtered_rentals)
        else:
            flash("There are no rentals that match that filter.")
            return redirect(url_for('Rentals.all_rentals'))
    except Exception as ex:
        print(ex)
        raise ex
    finally:
        con.close()
