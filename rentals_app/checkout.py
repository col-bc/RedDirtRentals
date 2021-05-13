from uuid import uuid1

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

import rentals_app.helpers as helpers
from rentals_app.auth import login_required

checkout = Blueprint('checkout', __name__, url_prefix='/checkout')



@checkout.route('/')
def index():
    return redirect(url_for('checkout.reserve', r_id=0))


# @checkout.route('/<int:r_id>/reserve')
# def reserve(r_id):
#     if g.user is None:
#         return redirect(url_for('auth.register'), next='')


# @checkout.route('/<int:r_id>/contact')
# def contact(r_id):
#     return render_template('checkout/contact.html', r_id=r_id)


@checkout.route('/<int:r_id>/<int:c_id>/dates/')
def dates(r_id, c_id):
    if r_id is not None and r_id >= 0:
        if c_id is not None and c_id >= 0:
            return render_template('checkout/dates.html', c_id=c_id,r_id=r_id)
        else:
            return redirect(url_for('Rentals.all_rentals'))
    else:
        flash('You need to select a rental and enter your information first. Try again, please.')


@checkout.route('/<int:r_id>/<int:c_id>/make_reservation', methods=['POST'])
def make_reservation(r_id, c_id):
    if r_id is not None and r_id >= 0:
        if c_id is not None and c_id >= 0:

            data = {
                "start_1": request.form.get('start_1'),
                "start_2": request.form.get('start_2'),
                "start_3": request.form.get('start_3'),
                "end_1": request.form.get('end_1'),
                "end_2": request.form.get('end_2'),
                "end_3": request.form.get('end_3'),
                "hours": request.form.get('hours_per_day')
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
            """.format(conf_no, r_id, c_id, data['start_1'], data['start_2'], data['start_3'],
                    data['end_1'], data['end_2'], data['end_3'], data['hours'])
            try:
                cur.execute(sql)
                con.commit()
                return redirect(url_for('checkout.confirmation', r_id=r_id, c_id=c_id, conf_no=conf_no))
            except Exception as ex:
                con.rollback()
                raise ex
    else:
        flash('Please select a rental first.')
        return redirect(url_for('Rentals.all_rentals'))
    

@checkout.route('/<int:r_id>/<int:c_id>/confirmation/<conf_no>')
def confirmation(r_id, c_id, conf_no):
    return render_template('checkout/confirmation.html', conf_no=conf_no)
