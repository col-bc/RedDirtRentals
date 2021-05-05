import rentals_app.helpers as helpers
from datetime import datetime

class Customer:
    
    def __init__(self, 
        customer_id:int = None,
        firstname:str = None, 
        lastname:str = None,
        address:str = None,
        city:str = None,
        state:str = None,
        zip:str = None,
        phonenumber:str = None,
        email:str = None,
        password:str = None,
        token_name:str = None,
        token:str = None,
        selected_inventory_id:int = None,
        selected_date_from:datetime.date = None,
        selected_date_to:datetime.date = None) -> None:
        self.customer_id = customer_id
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.phonenumber = phonenumber
        self.email = email
        self.password = password
        self.token_name = token_name
        self.token = token
        self.selected_inventory_id = selected_inventory_id
        self.selected_date_from = selected_date_from
        self.selected_date_to = selected_date_to


    def find_customer(id):
        con, cur = helpers.connect_to_db()
        sql = """
        SELECT * FROM customers WHERE id='{}';
        """.format(id)
        try:
            fetched = cur.execute(sql).fetchone()
            return Customer(
                customer_id=fetched[0],
                firstname=fetched[1],
                lastname=fetched[2],
                address=fetched[3],
                city=fetched[4],
                state=fetched[5],
                zip=fetched[6],
                phonenumber=fetched[7],
                email=fetched[8],
                password=fetched[9],
                token_name=fetched[10],
                token=fetched[11],
                selected_inventory_id=fetched[12],
                selected_date_from=fetched[13],
                selected_date_to=fetched[14]
            )
        except Exception as ex:
            raise ex
        finally:
            con.close()


    def insert(self) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
        INSERT OR IGNORE INTO customers (
            firstname,
            lastname,
            address,
            city,
            state,
            zip,
            phonenumber,
            email,
            password,
            token_name,
            token,
            selected_inventory_id,
            selected_date_from,
            selected_date_to
        )
        VALUES (
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
            '{10}',
            '{11}',
            '{12}',
            '{13}',
        );
        """.format(
            self.firstname,
            self.lastname,
            self.address,
            self.city,
            self.state,
            self.zip,
            self.phonenumber,
            self.email,
            self.password,
            self.token_name,
            self.token,
            self.selected_inventory_id,
            self.selected_date_from,
            self.selected_date_to
        )

        try: 
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()


    def update(obj, customer_id) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
        UPDATE customer SET 
            firstname='{0}',
            lastname='{1}',
            address='{2}',
            city='{3}',
            state='{4}',
            zip='{5}',
            phonenumber='{6}',
            email='{7}',
            password='{8}',
            token_name='{9}',
            token='{10}',
            selected_inventory_id='{11}',
            selected_date_from='{12}',
            selected_date_to='{13}'
        WHERE id='{14}'
        """.format(
            obj.firstname,
            obj.lastname,
            obj.address,
            obj.city,
            obj.state,
            obj.zip,
            obj.phonenumber,
            obj.email,
            obj.password,
            obj.token_name,
            obj.token,
            obj.selected_inventory_id,
            obj.selected_date_from,
            obj.selected_date_to,
            customer_id
        )

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()


    def delete(self) -> bool:
        con, cur = helpers.connect_to_db()
        sql = "DELETE * FROM customers WHERE id='{}'".format(self.customer_id)

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

