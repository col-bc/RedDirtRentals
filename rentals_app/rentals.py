import sqlite3
from flask import (
    url_for,
    redirect, 
    session, 
    Blueprint, 
    render_template,
)
from rentals_app.models.rental import Rental
import rentals_app.helpers as helpers

rentals = Blueprint('Rentals', __name__, url_prefix='/rentals')

@rentals.route('/')
def root():
    return redirect(url_for('rentals.all_rentals'))

@rentals.route('/all')
def all_rentals():
    con, cur = helpers.connect_to_db()
    ids = cur.execute('SELECT id FROM inventory WHERE is_shown == 1').fetchall()
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

    return render_template('rentals/index.html', rentals=rentals)

@rentals.route('/details/<int:id>', methods=['GET'])
def details(id):
    con, cur = helpers.connect_to_db()
    fetched_id = cur.execute("SELECT id FROM inventory WHERE id='{}';".format(id)).fetchone()
    rental = Rental().find_rental(fetched_id[0])
    
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
    
    return render_template('rentals/details.html', rental=rental)