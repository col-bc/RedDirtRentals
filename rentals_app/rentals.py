import sqlite3
from flask import (
    url_for,
    redirect, 
    session, 
    Blueprint, 
    render_template,
)
from flask.wrappers import Response
from rentals_app.helpers import connect_to_db

rentals = Blueprint('Rentals', __name__, url_prefix='/rentals')

@rentals.route('/')
def root():
    return redirect(url_for('rentals.all_rentals'))

@rentals.route('/all')
def all_rentals():
    con, cur = connect_to_db()
    rows = cur.execute('SELECT * FROM inventory WHERE is_shown == 1').fetchall()

    return render_template('rentals/index.html', rows=rows)