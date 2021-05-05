from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect
)

checkout = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout.route('/')
def index():
    return redirect(url_for())


@checkout.route('/checkout/reserve/<int:id>')
def reserve(id):

    return 200


@checkout.route('/checkout/customer/login')
def customer_login():

    return 200


@checkout.route('/checkout/customer/register', methods=['POST'])
def register():

    return 200


@checkout.route('/checkout/dates')
def dates():

    return 200


@checkout.route('/checkout/confirmation')
def confirmation():

    return 200