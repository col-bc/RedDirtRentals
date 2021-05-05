from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    request
)

checkout = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout.route('/')
def index():
    return redirect(url_for('checkout.contact', id=0))


@checkout.route('/checkout/<int:id>')
def reserve(id):

    return 200


@checkout.route('/checkout/<int:id>/contact')
def contact(id):
    return render_template('checkout/contact.html', id=id)


@checkout.route('/checkout/<int:id>/create_customer', methods=['POST'])
def create_customer(id):

    return redirect(url_for('checkout.dates'))


@checkout.route('/checkout/dates')
def dates():

    return 200


@checkout.route('/checkout/confirmation')
def confirmation():

    return 200