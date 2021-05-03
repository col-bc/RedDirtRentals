from flask import Blueprint
from flask import (
    url_for,
    redirect,
    render_template,
)


index = Blueprint('index', __name__, url_prefix='/')

@index.route('/')
def root():
    return render_template('index.html')

@index.route('/root/')
def application_root():
    return redirect(url_for('index.index'))
    
@index.route('/rd/main_site')
def send_to_rde():
    return redirect('https://reddirtequipment.com/')

