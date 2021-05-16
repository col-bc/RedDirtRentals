from rentals_app.models.rental import Rental
from rentals_app.auth import login_required
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)
from rentals_app.models.user import User
import rentals_app.helpers as helpers
from uuid import uuid1

account = Blueprint('account', __name__, url_prefix='/account')

@account.route('/')
@login_required
def index():
    return render_template('account/index.html', user=g.user)

@account.route('/reservations')
@login_required
def reservations():
    con, cur = helpers.connect_to_db()
    resv_sql = "SELECT * FROM reservations WHERE customer_id = '{}';".format(g.user.userid)
    try:
        reservations = cur.execute(resv_sql).fetchall()

        rental_ids = list()
        for x in reservations:
            rental_ids.append(x[2])
        
        rentals = dict()
        for id in rental_ids:
            rentals[str(id)] = Rental().find_rental(id)
            rentals[str(id)].image_paths = rentals[str(id)].image_paths[2:len(rentals[str(id)].image_paths)-2]


        return render_template('account/reservations.html', reservations=reservations, rentals=rentals)
    except Exception as ex:
        print(ex)
        raise ex
    finally:
        con.close()

@account.route('/reserve/<int:id>')
@login_required
def reserve(id):
    return render_template('account/reserve.html', id=id)

@account.route('/reserve/<int:r_id>/', methods=['POST'])
@login_required
def make_reservation(r_id):
    if r_id is not None and r_id >= 0:
        if g.user is not None:

            data = {
                "start_1": request.form.get('start_1'),
                "start_2": request.form.get('start_2'),
                "start_3": request.form.get('start_3'),
                "end_1": request.form.get('end_1'),
                "end_2": request.form.get('end_2'),
                "end_3": request.form.get('end_3'),
                "hours": request.form.get('usage_hours')
            }
            conf_no = uuid1()
            con, cur = helpers.connect_to_db()
            sql = """
            INSERT INTO RESERVATIONS (
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
            """.format(conf_no, r_id, g.user.userid, data['start_1'], data['start_2'], data['start_3'],
                    data['end_1'], data['end_2'], data['end_3'], data['hours'])
            try:
                cur.execute(sql)
                con.commit()
                return redirect(url_for('account.reserve_confirm', conf_no=conf_no))
            except Exception as ex:
                con.rollback()
                raise ex
    else:
        flash('Please select a rental first.')
        return redirect(url_for('account.reserve', conf_no=None))

@account.route('/reserve/confirm/<conf_no>')
@login_required
def reserve_confirm(conf_no):
    if conf_no:
        return render_template('account/confirm_reservation.html', conf_no=conf_no)
