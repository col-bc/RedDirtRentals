from flask import Blueprint
from flask import (
    url_for,
    redirect,
    render_template,
)
from rentals_app.models.rental import Rental
import rentals_app.helpers as helpers


index = Blueprint('index', __name__, url_prefix='/')

@index.route('/')
def root():
    con , cur = helpers.connect_to_db()
    ids = cur.execute("SELECT id FROM INVENTORY").fetchall()
    rentals = []
    for id_list in ids:
        for id in id_list:
            rentals.append(Rental().find_rental(id))
    for rental in rentals:
        rental.rate = float(rental.rate[0])
        rental.image_paths = list(
            rental.image_paths
                .replace('[','')
                .replace(']','')
                .replace("'",'')
                .split(',')
        )
        rental.implements = list(
            rental.implements
                .replace('[','')
                .replace(']','')
                .replace('\'','')
                .split(',')
        )

    return render_template('index.html', rentals = rentals)

@index.route('/root/')
def application_root():
    return redirect(url_for('index.index'))
    
