import sqlite3
import rentals_app.helpers as helpers

class User():

    def __init__(self,
            userid:int=None,
            firstname:str=None,
            lastname:str=None,
            phonenumber:str=None,
            email:str=None,
            password:str=None,
            address:str=None,
            city:str=None,
            state:str=None,
            zip:str=None) -> None:
        self.userid=userid
        self.firstname=firstname
        self.lastname=lastname
        self.phonenumber=phonenumber
        self.email=email
        self.password=password
        self.address=address
        self.city=city
        self.state=state
        self.zip=zip

    def find_user(id):
        con, cur = helpers.connect_to_db()
        sql ="""
        SELECT * FROM users WHERE id='{}'
        """.format(id)

        try:
            db = cur.execute(sql).fetchone()
            con.commit()
            return User(
                userid=db[0],
                firstname=db[1],
                lastname=db[2],
                phonenumber=db[3],
                email=db[4],
                password=db[5],
                address=db[6],
                city=db[7],
                state=db[8],
                zip=db[9]
            )
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

    def create_user(new):
        con, cur = helpers.connect_to_db()
        sql = """
        INSERT INTO users (
            firstname,
            lastname,
            phonenumber,
            email,
            password,
            address,
            city,
            state,
            zip
        ) VALUES (
            {0},
            {1},
            {2},
            {3},
            {4},
            {5},
            {6},
            {7},
            {8}
        )
        """.format(
            new.firstname,
            new.lastname,
            new.phonenumber,
            new.email,
            new.password,
            new.address,
            new.city,
            new.state,
            new.zip
        )

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex

    def update_user(id, new):
        cur, con = helpers.connect_to_db()
        sql = """
        UPDATE users SET
            firstname='{}',
            lastname='{1}',
            phonenumber='{2}',
            email='{3}',
            password='{4}',
            address='{5}',
            city='{6}',
            state='{7}',
            zip='{8}'
        WHERE userid='{9}'
        """.format(
            new.firstname,
            new.lastname,
            new.phonenumber,
            new.email,
            new.password,
            new.address,
            new.city,
            new.state,
            new.zip,
            id
        )

    def delete_user(self):
        cur, con = helpers.connect_to_db()
        sql = "DELETE FROM users WHERE userid='{}'".format(self.userid)

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()
