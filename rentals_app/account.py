from rentals_app.auth import login_required
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)
from rentals_app.models.user import User
import rentals_app.helpers as helpers

account = Blueprint('account', __name__, url_prefix='/account')

@account.route('/')
@login_required
def index():
    return render_template('account/index.html', user=g.user)
