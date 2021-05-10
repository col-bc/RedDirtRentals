import functools
from functools import wraps
import hashlib
import datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)

auth = Blueprint('auth', __name__, url_prefix='/auth')
EVENT_LOG = '/Users/colby/RedDirtRentals/events.log'

@auth.before_app_request
def fetch_current_user():
    if g.userid is not None:
        
    else:
        session['status'] = 'FAILED'

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        IS_AUTHENTICATED = session.get('status') == 'AUTHENTICATED'
        IS_EXPIRED = session.get('expire') is not None and session.get('expire') < datetime.datetime.now()
        # Force Login if not authenticated
        if not IS_AUTHENTICATED:
            session.pop('status')
            flash('You must be logged in to view that page.')
            return redirect(url_for('auth.login'))
        # Kill Session if Expired
        if IS_EXPIRED:
            session.pop('username')
            session['status'] = 'FAILED'
            session.pop('IS_ADMIN')
            flash('Please reverify your credentials.')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@auth.route('/')
def root():
    return redirect('login')

@auth.route('/login')
def login():
    return render_template('auth/login.html')

HASH = '5b39916ae093f507183c31b11d46da9baa1305a3c27f7129eb441fa30f017bb6'
USR = 'reddirt'
ADMIN_USR = 'admin'
ADMIN_HASH = 'b64154c3b86eebbe5b353f76f9f811648654172c3e7ead77d0182bdf2af1c429'

@auth.route('/verify', methods=['GET', 'POST'])
def auth_admin():
    username = str(request.form.get('username')).lower()
    password = request.form.get('passwd')

    if username == ADMIN_USR and hashlib.sha256(password.encode()).hexdigest() == ADMIN_HASH:
        session['IS_ADMIN'] = 'TRUE'
        session['username'] = 'admin'
        session['status'] = 'AUTHENTICATED'
        with open(EVENT_LOG, 'a+') as log:
            log.write('[{0}] Admin session spawned from {1}\n'.format(datetime.datetime.now(), request.remote_addr))
            log.close()
        session['expire'] = datetime.datetime.now() + datetime.timedelta(hours=1)
        return redirect(url_for('admin.inventory'))

    elif username == USR and hashlib.sha256(password.encode()).hexdigest() == HASH:
        session['IS_ADMIN'] = 'FALSE'
        session['username'] = 'reddirt'
        session['status'] = 'AUTHENTICATED'
        return redirect(url_for('admin.inventory'))

    else:
        flash('The supplied credentials are invalid. This event has been recorded.')
        with open(EVENT_LOG, 'a+') as ev_log:
            ev_log.write('[{0}] Login failure from {1} * {2}:{3}\n'.format(datetime.datetime.now(), request.remote_addr, username, password))
            ev_log.close()
        session['status'] = 'FAILED'
        return redirect(url_for('auth.login'))
    
@auth.route('/logout')
def logout():
    session.pop('status')
    session.pop('username')
    session.pop('IS_ADMIN')
    return redirect('/')
