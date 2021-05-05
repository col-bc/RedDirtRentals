from flask import (
    Flask, render_template
)

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'development*041921'


from . import index
app.register_blueprint(index.index)

from . import auth
app.register_blueprint(auth.auth)

from . import admin
app.register_blueprint(admin.admin)

from . import rentals
app.register_blueprint(rentals.rentals)

from . import checkout
app.register_blueprint(checkout.checkout)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warn(e)
    return render_template('errors/404.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')


