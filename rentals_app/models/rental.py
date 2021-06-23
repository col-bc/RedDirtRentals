import os
import datetime
import rentals_app.helpers as helpers
from flask import current_app
from werkzeug.utils import secure_filename


# Functions that return bool indicating
# if sql executed successfully.
class Rental:

    # Will raise sqlite3 exception unless
    # changed by function.
    rental_id = -1

    # Default Constructor
    def __init__(
        self,
        rental_id: int = None,
        category: str = None,
        make: str = None,
        model: str = None,
        fuel_type: str = None,
        horse_power: str = None,
        deck_size: str = None,
        implements: str = None,
        stock: str = None,
        drive: str = None,
        rate: float = None,
        image_paths: str = None,
        job_category: str = None,
        price_range: str = None,
        is_available: int = 1,
        available_on: datetime.date = None,
        rented_by: str = None,
        rent_queue: str = None,
        is_shown: int = 0,
        description: str = None,
        features: str = None,
    ) -> None:
        self.rental_id = rental_id
        self.category = category
        self.make = make
        self.model = model
        self.fuel_type = fuel_type
        self.horse_power = horse_power
        self.deck_size = deck_size
        self.implements = implements
        self.stock = stock
        self.drive = drive
        self.rate = (rate,)
        self.image_paths = image_paths
        self.job_category = job_category
        self.price_range = price_range
        self.is_available = is_available
        self.available_on = available_on
        self.rented_by = rented_by
        self.rent_queue = rent_queue
        self.is_shown = is_shown
        self.description = description
        self.features = features

    def __str__(self) -> str:
        return str(
            dict(
                {
                    "rental_id": self.rental_id,
                    "category": self.category,
                    "make": self.make,
                    "model": self.model,
                    "fuel_type": self.fuel_type,
                    "horse_power": self.horse_power,
                    "deck_size": self.deck_size,
                    "implements": self.implements,
                    "stock": self.stock,
                    "drive": self.drive,
                    "rate": self.rate,
                    "image_paths": self.image_paths,
                    "job_category": self.job_category,
                    "price_range": self.price_range,
                    "is_available": self.is_available,
                    "available_on": self.available_on,
                    "rented_by": self.rented_by,
                    "rent_queue": self.rent_queue,
                    "is_shown": self.is_shown,
                    "description": self.description,
                    "features": self.features,
                }
            )
        )

    # Returns Rental Object from rental id
    def find_rental(self, rental_id) -> "Rental":
        con, cur = helpers.connect_to_db()
        try:
            result = cur.execute(
                """ SELECT * FROM inventory WHERE id="{}";""".format(rental_id)
            ).fetchone()
            if not result:
                return None 

            rental = Rental(
                rental_id=result[0],
                category=result[1],
                make=result[2],
                model=result[3],
                fuel_type=result[4],
                horse_power=result[5],
                deck_size=result[6],
                implements=result[7],
                stock=result[8],
                drive=result[9],
                rate=result[10],
                image_paths=result[11],
                job_category=result[12],
                price_range=result[13],
                is_available=result[14],
                available_on=result[15],
                rented_by=result[16],
                rent_queue=result[17],
                is_shown=result[18],
                description=result[19],
                features=result[20],
            )
            return rental
        except Exception as ex:
            print(ex)
            raise ex
        finally:
            con.close()

    # Insert new Rental into DB
    def insert(data) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
        INSERT INTO inventory (
            category,       
            make,           
            model,          
            fuel_type,      
            horsepower,     
            deck_size,      
            implements,     
            stock,          
            drive,          
            rate,           
            image_paths,    
            job_category,   
            price_range,    
            is_available,   
            available_on,   
            rented_by,      
            rent_queue,     
            is_shown,       
            description,    
            features        
        ) VALUES (
            "{0}",
            "{1}",
            "{2}",
            "{3}",
            "{4}",
            "{5}",
            "{6}",
            "{7}",
            "{8}",
            "{9}",
            "{10}", 
            "{11}",
            "{12}", 
            "{13}", 
            "{14}",
            "{15}", 
            "{16}", 
            "{17}", 
            "{18}", 
            "{19}" 
        );
        """.format(
            data.category,
            data.make.replace('"', ""),
            data.model.replace('"', ""),
            data.fuel_type,
            data.horse_power,
            data.deck_size.replace('"', ""),
            data.implements,
            data.stock,
            data.drive,
            data.rate,
            data.image_paths,
            data.job_category,
            data.price_range,
            data.is_available,
            data.available_on,
            data.rented_by,
            data.rent_queue,
            data.is_shown,
            data.description.replace('"', ""),
            data.features.replace('"', ""),
        )
        print(sql)
        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

    # Update record of current instance
    def update(data, rental_id) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
        UPDATE INVENTORY 
        SET
            category="{0}",
            make="{1}", 
            model="{2}",
            fuel_type="{3}", 
            horsepower="{4}",
            deck_size="{5}", 
            implements="{6}",
            stock="{7}", 
            drive="{8}",
            rate="{9}", 
            image_paths="{10}",
            job_category="{11}", 
            price_range="{12}", 
            is_available="{13}", 
            available_on="{14}", 
            rented_by="{15}", 
            rent_queue="{16}", 
            is_shown="{17}", 
            description='{18}', 
            features="{19}"
        WHERE
            id='{20}';
        """.format(
            data.category,
            data.make,
            data.model,
            data.fuel_type,
            data.horse_power,
            data.deck_size,
            data.implements,
            data.stock,
            data.drive,
            data.rate,
            data.image_paths,
            data.job_category.replace('"', ""),
            data.price_range,
            data.is_available,
            data.available_on,
            data.rented_by,
            data.rent_queue,
            data.is_shown,
            data.description.replace('"', ""),
            data.features.replace('"', ""),
            rental_id,
        )
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
        sql = """
        DELETE FROM 
            inventory
        WHERE id='{0}';
        """.format(
            self.rental_id
        )
        try:
            con, cur = helpers.connect_to_db()
            cur.execute(sql)
            con.commit()
            print("Rental #{} Deleted".format(self.rental_id))
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
            abs_path = helpers.RENTAL_IMAGE_PATH + "/{0}_{1}_{2}".format(
                self.make, self.model, self.category
            )
            os.removedirs(abs_path)
            return True
        except IOError:
            return False

    # Update is_rented for current instance
    def set_is_rented(self, is_rented) -> bool:
        try:
            con, cur = helpers.connect_to_db()
            cur.execute(
                """
            UPDATE 
                inventory 
            SET 
                is_rented='{0}' 
            WHERE id='{1}';""".format(
                    (1 if is_rented else 0), self.rental_id
                )
            )
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
            cur.execute(
                """
            UPDATE 
                inventory 
            SET 
                available_on='{0}' 
            WHERE id='{1}';""".format(
                    available_on, self.rental_id
                )
            )
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
            cur.execute(
                """
            UPDATE 
                inventory 
            SET 
                rented_by='{0}' 
            WHERE id='{1}';""".format(
                    (1 if name is not None else 0), self.rental_id
                )
            )
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
            current = cur.execute(
                """
            SELECT
                rent_queue
            FROM 
                inventory
            WHERE id='{0}';
            """.format(
                    self.rental_id
                )
            )

            cur.execute(
                """
            UPDATE
                inventory 
            SET 
                is_rented='{0}'
            WHERE id='{1}';""".format(
                    "{0}, {1}".format(current, name), self.rental_id
                )
            )

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
            cur.execute(
                """
            UPDATE
                users 
            SET 
                rent_queue='' 
            WHERE id='{1}';""".format(
                    rental_id
                )
            )

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
            cur.execute(
                """
            UPDATE 
                users 
            SET 
                is_shown='{0}' 
            WHERE id='{1}';""".format(
                    1 if visibility is True else 0, self.rental_id
                )
            )
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
