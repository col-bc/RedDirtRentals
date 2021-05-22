from flask import (
    Flask, render_template
)

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'development*041921'

app.config['MAIL_SERVER']='outlook.office365.com'
app.config['MAIL_PORT'] = 993
app.config['MAIL_USERNAME'] = 'ccooper@reddirtequipment.com'
app.config['MAIL_PASSWORD'] = 'Av3ryJ4x!0711#'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

from . import auth
app.register_blueprint(auth.auth)

from . import admin
app.register_blueprint(admin.admin)

from . import rentals
app.register_blueprint(rentals.rentals)

from . import index
app.register_blueprint(index.index)

from . import account
app.register_blueprint(account.account)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warn(e)
    return render_template('errors/404.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')


