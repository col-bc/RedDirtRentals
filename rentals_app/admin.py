import datetime
import os
import sqlite3

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)

import rentals_app.helpers as helpers
from rentals_app.auth import login_required
from rentals_app.models.rental import *

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def root():
    return redirect(url_for('admin.inventory'))

# Render index page
@admin.route('/inventory')
@login_required
def inventory():
    con, cur = helpers.connect_to_db()
    ids = list(cur.execute("SELECT id FROM inventory;").fetchall())
    rentals = []
    for id_list in ids:
        for id in id_list:
            rentals.append(Rental().find_rental(id))
    for rental in rentals:
        rental.implements = list(
            rental.implements
                .replace('[','')
                .replace(']','')
                .replace('\'','')
                .split(',')
        )
        rental.image_paths = list(
            rental.image_paths
                .replace('[','')
                .replace(']','')
                .replace("'",'')
                .split(',')
        )

    con.close

    return render_template('admin/index.html', rentals=rentals)


# Render New page
@admin.route('/new')
@login_required
def new():
    return render_template('admin/new.html')


#### CRUD FUNCTIONS ####
# - CREATE
@admin.route('/new/create/', methods=['POST', 'GET'])
@login_required
def create():
    rental = Rental()
    if request.method == 'POST':

        rental.category =       request.form.get('category')
        rental.make =           request.form.get('make')
        rental.model =          request.form.get('model')
        rental.fuel_type =      request.form.get('fuel_type')
        rental.horse_power =    request.form.get('horse_power')
        rental.deck_size =      request.form.get('deck_size')
        rental.implements =     request.form.getlist('implements')
        rental.stock =          request.form.get('stock')
        rental.rate =           float(request.form.get('rate'))
        rental.drive =          request.form.get('drive')
        rental.job_category =   request.form.get('job_category')
        rental.price_range =    request.form.get('price_range')
        rental.is_available =   1 if request.form.get('is_available') == 'Yes' else 0
        rental.available_on =   datetime.datetime.strptime(request.form.get('available_on'), '%Y-%m-%d').date()
        rental.rented_by =      request.form.get('rented_by')
        rental.rent_queue =     request.form.get('rent_queue')
        rental.is_shown =       1 if request.form.get('is_shown') == 'Yes' else 0
        rental.description =    request.form.get('description')
        rental.features =       request.form.get('features')

        paths = []
        files = request.files.getlist('files')
        for file in files:
            if file:
                folder_format = '/{0}_{1}_{2}/'.format(rental.make,rental.model,rental.category)
                filename = secure_filename(file.filename)
                file.save(helpers.ABS_UPLOAD_PATH+folder_format+'/'+filename)
                paths.append(os.path.join(
                    current_app.static_url_path,
                    folder_format+filename))
        rental.image_paths=paths
    
        if rental.insert():
            return redirect(url_for('admin.inventory'))
        else:
            flash('Could not add rental. Please try again.')
            return redirect(url_for('admin.inventory'))


# CRUD - READ
@admin.route('/details/<int:id>')
@login_required
def details(id):
    rental = Rental().find_rental(rental_id=id)
    rental.image_paths = list(
            rental.image_paths
                .replace('[','')
                .replace(']','')
                .replace("'",'')
                .split(',')
        )
    rental.implements = list(rental.implements.replace('[','').replace(']','').replace('\'','').split(','))
    return render_template('admin/details.html', rental=rental)


# CRUD - UPDATE
@admin.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    rental = Rental()
    if request.method == 'POST':
        rental.category =       request.form.get('category')
        rental.make =           request.form.get('make')
        rental.model =          request.form.get('model')
        rental.fuel_type =      request.form.get('fuel_type')
        rental.horse_power =    request.form.get('horse_power')
        rental.deck_size =      request.form.get('deck_size')
        rental.implements =     request.form.getlist('implements')
        rental.stock =          request.form.get('stock')
        rental.rate =           float(request.form.get('rate'))
        rental.drive =          request.form.get('drive')
        rental.job_category =   request.form.get('job_category')
        rental.price_range =    request.form.get('price_range')
        rental.is_available =   1 if request.form.get('is_available') == 'Yes' else 0
        rental.available_on =   datetime.datetime.strptime(request.form.get('available_on'), '%Y-%m-%d').date()
        rental.rented_by =      request.form.get('rented_by')
        rental.rent_queue =     request.form.get('rent_queue')
        rental.is_shown =       1 if request.form.get('is_shown') == 'Yes' else 0
        rental.description =    request.form.get('description')
        rental.features =       request.form.get('features')

        paths = []
        files = request.files.getlist('files')
        for file in files:
            if file:
                folder_format = '/{0}_{1}_{2}/'.format(rental.make,rental.model,rental.category)
                if not os.path.exists(helpers.ABS_UPLOAD_PATH+folder_format):
                    os.mkdir(helpers.ABS_UPLOAD_PATH+folder_format)

                filename = secure_filename(file.filename)
                file.save(helpers.ABS_UPLOAD_PATH+folder_format+'/'+filename)
                paths.append(os.path.join(
                    current_app.static_url_path,
                    folder_format+filename))
        rental.image_paths = paths

        if Rental.update(rental, id):
            flash('Record #'+str(id)+' was successfully updated')
            return redirect(url_for('admin.details',id=id))
        else:
            flash('Something went wrong while updating record #{}. Please try again.'.format(id))
            return redirect(url_for('admin.inventory'))


# CRUD - DELETE
@admin.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if Rental().find_rental(id).delete():
        flash('Record #'+str(id)+' successfully deleted.')
        return redirect(url_for('admin.inventory'))
    else: 
        flash('Something went wrong while deleting record #{}. Please contact your administrator.'.format(id))
        return redirect(url_for('admin.inventory'))

# Run sql from browser, if permitted by group
@admin.route('/new/fast_add', methods=['GET','POST'])
def fast_add():
    print('Executing admin sql query\n{0}'.format(request.form.get('sql_query')))
    helpers.log_event('[{0}] Admin executed sql from {1}\n'.format(datetime.datetime.now(), request.remote_addr))
    try:
        con, cur = helpers.connect_to_db()
        cur.execute(request.form.get('sql_query'))
        con.commit()
    except Exception as ex:
        con.rollback()
        flash(ex)
    finally:
        con.close()
        return redirect(url_for('admin.inventory'))


