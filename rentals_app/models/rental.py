import os
import uuid

import rentals_app.helpers as helpers
from flask import current_app
from werkzeug.utils import secure_filename


# Functions that return bool indiate
# if sql executed successfully.
class Rental:

    # Will raise sqlite3 exception unless
    # changed by function.
    rental_id = -1


    # Default Constructor
    def __init__(self,
        make=None,
        model=None,
        category=None,
        fuel_type=None,
        horsepower=None,
        decksize=None,
        engine=None,
        stock=None,
        drive=None,
        rate=None,
        job_category=None,
        price_range=None,
        rented_by=None,
        rent_queue=None,
        description=None,
        features=None,
        available_on=None,
        image_paths=None,
        is_available = True,
        is_shown = True,
        rental_id=None):
            self.make=make
            self.model=model 
            self.category=category 
            self.fuel_type=fuel_type
            self.horsepower=horsepower
            self.decksize=decksize
            self.engine=engine
            self.stock=stock
            self.drive=drive
            self.rate=rate
            self.job_category=job_category
            self.price_range=price_range
            self.rented_by=rented_by
            self.rent_queue=rent_queue
            self.description=description
            self.features=features
            self.is_available=is_available,
            self.is_shown=is_shown,
            self.rental_id=rental_id,
            self.image_paths = image_paths,
            self.available_on = available_on


    # Returns Rental Object from rental id
    def find_rental(self, rental_id):
        con, cur = helpers.connect_to_db()
        try:
            result =cur.execute("SELECT * FROM inventory WHERE id='{0}'"
                .format(rental_id)).fetchone()
            rental =  Rental(
                rental_id = result[0],
                category = result[1],
                make= result[2],
                model = result[3],
                fuel_type = result[4],
                horsepower = result[5],
                decksize = result[6],
                engine = result[7],
                stock = result[8],
                drive = result[9],
                rate = result[10],
                image_paths = result[11],
                job_category = result[12],
                price_range = result[13],
                is_available = result[14] == 1,
                rented_by = result[15],
                rent_queue = result[16],
                is_shown = result[17] == 1,
                description = result[18],
                features = result[19]
            )
            print(rental.rental_id)
            return rental
        except Exception as ex:
            print(ex)
            raise ex
        finally: 
            con.close()


    # Insert new Rental into DB
    def insert(obj) -> bool:
        try:
            assert type(obj) is Rental
        except AssertionError:
            raise AssertionError

        con, cur = helpers.connect_to_db()
        try:
            cur.execute("""
                INSERT INTO inventory (
                    make,
                    model,
                    category,
                    fuel_type,
                    horsepower,
                    deck_size,
                    engine,
                    stock,
                    drive,
                    rate,
                    image_paths,
                    job_category,
                    price_range,
                    is_available,
                    rented_by,
                    rent_queue,
                    is_shown,
                    description,
                    features,
                    available_on
                ) VALUES (
                    '{0}',
                    '{1}',
                    '{2}',
                    '{3}',
                    '{4}',
                    '{5}',
                    '{6}',
                    '{7}',
                    '{8}',
                    '{9}',
                    "{10}",
                    '{11}',
                    '{12}',
                    '{13}',
                    '{14}',
                    '{15}',
                    '{16}',
                    '{17}',
                    '{18}',
                    '{19}'
                );
            """.format(obj.make, obj.model, obj.category,
                obj.fuel_type[0], obj.horsepower, obj.decksize,
                obj.engine, obj.stock, obj.drive, obj.rate,
                obj.image_paths, obj.job_category, obj.price_range,
                obj.is_available, obj.rented_by, obj.rent_queue,
                obj.is_shown, obj.description, obj.features, obj.available_on))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()


    # Update record of current instance
    def update(obj, rental_id) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
                UPDATE inventory SET
                    make='{0}',
                    model='{1}',
                    category='{2}',
                    fuel_type='{3}',
                    horsepower='{4}',
                    deck_size='{5}',
                    engine='{6}',
                    stock='{7}',
                    drive='{8}',
                    rate='{9}',
                    image_paths="{10}",
                    job_category='{11}',
                    price_range='{12}',
                    is_available='{13}',
                    rented_by='{14}',
                    rent_queue='{15}',
                    is_shown='{16}',
                    description='{17}',
                    features='{18}'
                WHERE id='{19}';
            """.format(obj.make, obj.model, obj.category,
                obj.fuel_type[0], obj.horsepower, obj.decksize,
                obj.engine, obj.stock, obj.drive, obj.rate,
                obj.image_paths, obj.job_category, obj.price_range,
                obj.is_available, obj.rented_by, obj.rent_queue,
                obj.is_shown, obj.description, obj.features, rental_id)
        print(sql)
        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Delete current instance from DB
    def delete(self) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("DELETE FROM inventory WHERE id='{0}';".format(self.rental_id[0]))
            con.commit()
            print('Rental #{} Deleted'.format(self.rental_id))
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Deletes images from server for current instance
    def delete_images(self) -> bool:
        try:
            abs_path = helpers.RENTAL_IMAGE_PATH+'/{0}_{1}_{2}'.format(self.make, self.model, self.category)
            os.removedirs(abs_path)
            return True
        except IOError:
            return False


    # Update is_rented for current instance
    def set_is_rented(self, is_rented) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("UPDATE users SET is_rented='{0}' WHERE id='{1}';"
                .format((1 if is_rented else 0), self.rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Update date_available for current instance
    def set_date_available(self, available_on) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("UPDATE users SET available_on='{0}' WHERE id='{1}';"
                .format(available_on, self.rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Update rented_by for current instance
    def set_rented_by(self, name) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("UPDATE users SET rented_by='{0}' WHERE id='{1}';"
                .format((1 if name else 0), self.rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()
          

    # Appends parameter `name` to end of rental_queue
    # for current instance
    def add_to_queue(self, name) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            current = cur.execute("SELECT rent_queue FROM users WHERE id='{0}';".format(self.rental_id))
            cur.execute("UPDATE users SET is_rented='{0}' WHERE id='{1}';"
                .format("{0}, {1}".format(current, name), self.rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Clears the queue for current instance
    def clear_queue(self, rental_id) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("UPDATE users SET rent_queue='' WHERE id='{1}';"
                .format(rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Sets visibility of rental to customer for current instance
    def set_visibility(self, visibility) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute("UPDATE users SET is_shown='{0}' WHERE id='{1}';"
                .format(1 if visibility is True else 0, self.rental_id))
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            print(ex)
            return False
        finally:
            con.close()


    # Returns object with same data for modification
    def clone(self, rental):
        return Rental(rental)
        
