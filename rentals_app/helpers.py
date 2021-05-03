import sqlite3
from rentals_app.models.rental import Rental

RENTAL_IMAGE_PATH = '/Users/colby/RedDirtRentals/rentals_app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'tiff', 'jpeg'}


def connect_to_db():
    con = sqlite3.connect('/Users/colby/RedDirtRentals/database.db')
    return con, con.cursor()


def run_sql(qry,args=''):
    con = sqlite3.connect('/Users/colby/RedDirtRentals/database.db')
    result = con.cursor().execute(qry,args)
    con.commit()
    if result != None:
        con.close()
        return result
    con.close()
    return False


def get_attributes(request):
    return { # dict with request objects
        "make": request.form.get("make"),
        "model": request.form.get("model"),
        "fuel_type": request.form.get("fuel_type"),
        "category": request.form.get("category"),
        "job_category": request.form.get("job_category"),
        "horsepower": request.form.get("horsepower"),
        "deck_size": request.form.get("deck_size"),
        "engine": request.form.get("engine"),
        "stock": request.form.get("stock"),
        "drive": request.form.get("drive"),
        "rate": request.form.get("rate"),
        "price_range": request.form.get("price_range"),
        "rented_by": request.form.get("rented_by_name"),
        "date_available": request.form.get("date_available"),
        "rent_queue": request.form.get("queue"),
        "is_shown": request.form.get("is_customer_facing"),
        "image": request.form.get("files"),
        "features": request.form.get("features"),
        "is_available": request.form.get("is_currently_available"),
        "description": request.form.get("description"),
    }


def log_event(msg):
    with open('/Users/colby/RedDirtRentals/events.log', 'a+') as log:
        log.write(msg)
        log.close()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


