from flask import Flask, render_template, session, g
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from flask_wtf.csrf import CSRFError


app = Flask(__name__, instance_relative_config=True)
app.secret_key = "development*041921"

app.PERMANENT_SESSION_LIFETIME = timedelta(seconds=30)
app.SESSION_REFRESH_EACH_REQUEST = True


app.WTF_CSRF_SECRET_KEY = "development*061121"
csrf = CSRFProtect()
csrf.init_app(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    session.clear()
    g.user = None
    return render_template("errors/401.html", reason=e.description), 401


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
    return render_template("errors/404.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
