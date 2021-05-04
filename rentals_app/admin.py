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
    con.row_factory = sqlite3.Row
    cur.execute('SELECT * FROM inventory WHERE 1=1')
    rows = cur.fetchall()

    con.close()

    return render_template('admin/index.html', rows=rows)


# Render New page
@admin.route('/new')
@login_required
def new():
    return render_template('admin/new.html')


#### CRUD FUNCTIONS ####
# CREATE
@admin.route('/new/create/', methods=['POST', 'GET'])
@login_required
def create():
    rental = Rental()
    attr = helpers.get_attributes(request)
    if request.method == 'POST':

        print(helpers.get_attributes(request))

        

        
        print(rental)
    
        if rental.insert():
            return redirect(url_for('admin.inventory'))
        else:
            flash('Could not add rental. Please try again.')
            return redirect(url_for('admin.inventory'))


# CRUD READ
@admin.route('/details/<int:id>')
@login_required
def details(id):
    rental = Rental().find_rental(rental_id=id)
    paths = []
    images = rental.image_paths
    for image in images:
        paths.append(image.replace('[','').replace(']','').replace('\'','').split(','))
    return render_template('admin/details.html', rental=rental, images=paths)


# CRUD UPDATE
@admin.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    attr = helpers.get_attributes(request)
    rental = Rental()

    is_shown = True
    if attr['is_shown'] == 'No':
        is_shown = False

    if request.method == 'POST':
        rental.category= attr['category'] 
        rental.make = attr['make']
        rental.model = attr['model']
        rental.fuel_type = attr['fuel_type'],
        rental.horsepower = attr['horsepower']
        rental.decksize = attr['deck_size']
        rental.engine = attr['engine']
        rental.stock = attr['stock']
        rental.drive = attr['drive']
        rental.rate = attr['rate']
        rental.job_category = attr['job_category']
        rental.price_range = attr['price_range']
        rental.is_available = attr['is_available']
        rental.available_on = attr['date_available']
        rental.rented_by = attr['rented_by']
        rental.rent_queue = attr['rent_queue']
        rental.description = attr['description']
        rental.feature = attr['features']
        rental.is_shown = 1 if is_shown is True else 0

        files = request.files.getlist('rental_image')
        relative_paths = []
        abs_path = helpers.RENTAL_IMAGE_PATH+'/{0}_{1}_{2}/'.format(rental.make, rental.model, rental.category)

        if not os.path.exists(abs_path):
            os.mkdir(abs_path)
            print('Creating dir {}'.format(abs_path))

        for file in files: 
            filename = secure_filename(file.filename)
            file.save(abs_path+'/'+filename)
            relative_paths.append(current_app.static_url_path+'/uploads/{0}_{1}_{2}/'.format(rental.make, rental.model, rental.category)+filename)
            print('Appending to paths -> {}'.format(relative_paths[len(relative_paths)]))
        rental.image_paths = relative_paths

        if Rental.update(rental, id):
            flash('Record #'+str(id)+' was successfully updated')
            return redirect(url_for('admin.inventory'))
        else:
            flash('Something went wrong while updating record #{}. Please try again.'.format(id))
            return redirect(url_for('admin.inventory'))


# CRUD DELETE
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


