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
    return redirect(url_for('checkout.reserve', id=0))


@checkout.route('/<int:id>')
def reserve(id):
    if id is not None and id > 0:
        return redirect(url_for('checkout.contact', id=id))
    else:
        return redirect(url_for('Rentals.all_rentals'))


@checkout.route('/<int:id>/contact')
def contact(id):
    return render_template('checkout/contact.html', id=id)


@checkout.route('/<int:id>/create_customer', methods=['POST'])
def create_customer(id):
    return redirect(url_for('checkout.dates'))


@checkout.route('/<int:id>/dates')
def dates(id):
    if id is not None and id > 0:
        return render_template('checkout/dates.html', id=id)
    else:
        return redirect(url_for('Rentals.all_rentals'))



@checkout.route('/confirmation')
def confirmation():

    return 200