from flask import Flask, render_template, session, g
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from flask_wtf.csrf import CSRFError
from . import auth, admin, rentals, index, account


app = Flask(__name__, instance_relative_config=True)
app.secret_key = "development*041921"

app.PERMANENT_SESSION_LIFETIME = timedelta(seconds=30)
app.SESSION_REFRESH_EACH_REQUEST = True

# setup CSRF protection.
app.WTF_CSRF_SECRET_KEY = "development*061121"
csrf = CSRFProtect()
csrf.init_app(app)
# render 401 for csrf err
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    session.clear()
    g.user = None
    return render_template("errors/401.html", reason=e.description), 401


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warn(e)
    return render_template("errors/404.html")

# prevent page cacheing
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# register blueprints
app.register_blueprint(auth.auth)
app.register_blueprint(admin.admin)
app.register_blueprint(rentals.rentals)
app.register_blueprint(index.index)
app.register_blueprint(account.account)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
