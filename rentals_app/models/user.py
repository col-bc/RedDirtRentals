from flask.globals import current_app
import rentals_app.helpers as helpers


class User:
    def __init__(
        self,
        userid: int = None,
        firstname: str = None,
        lastname: str = None,
        phonenumber: str = None,
        email: str = None,
        password: str = None,
        groups: str = None,
        address: str = None,
        city: str = None,
        state: str = None,
        zip: str = None,
    ) -> None:
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.phonenumber = phonenumber
        self.email = email
        self.password = password
        self.groups = groups
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip

    def find_user(id) -> "User":
        """Searches database for user with provided id. Returns user object"""
        con, cur = helpers.connect_to_db()
        sql = """
        SELECT * FROM users WHERE id='{}'
        """.format(
            id
        )

        try:
            db = cur.execute(sql).fetchone()
            if not db:
                return None
            return User(
                userid=db[0],
                firstname=db[1],
                lastname=db[2],
                phonenumber=db[3],
                email=db[4],
                password=db[5],
                groups=db[6],
                address=db[7],
                city=db[8],
                state=db[9],
                zip=db[10],
            )
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

    def find_user_by_email(email) -> "User":
        """Searches database for user with provided email. Returns user object"""
        con, cur = helpers.connect_to_db()
        sql = """
        SELECT * FROM users WHERE email='{}';
        """.format(
            email
        )
        try:
            db = cur.execute(sql).fetchone()
            if not db:
                return None
            return User(
                userid=db[0],
                firstname=db[1],
                lastname=db[2],
                phonenumber=db[3],
                email=db[4],
                password=db[5],
                groups=db[6],
                address=db[7],
                city=db[8],
                state=db[9],
                zip=db[10],
            )
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

    def create_user(self) -> bool:
        """Inserts user data into database"""
        con, cur = helpers.connect_to_db()
        sql = """
        INSERT INTO users (
            firstname,
            lastname,
            phonenumber,
            email,
            password,
            groups,
            address,
            city,
            state,
            zip
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
            "{9}"
        )
        """.format(
            self.firstname,
            self.lastname,
            self.phonenumber,
            self.email,
            self.password,
            self.groups,
            self.address,
            self.city,
            self.state,
            self.zip,
        )

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex

    def update_user(id, new) -> bool:
        """Updates user's data with matching id.
        `New` data overwrites existing data.
        Returns true if successful"""
        con, cur = helpers.connect_to_db()
        SQL = """
        UPDATE users SET
            firstname='{0}',
            lastname='{1}',
            phonenumber='{2}',
            email='{3}',
            password='{4}',
            groups='{5}',
            address='{6}',
            city='{7}',
            state='{8}',
            zip='{9}'
        WHERE id='{10}'
        """.format(
            new.firstname,
            new.lastname,
            new.phonenumber,
            new.email,
            new.password,
            new.groups,
            new.address,
            new.city,
            new.state,
            new.zip,
            new.userid,
        )
        print(SQL)
        try:
            cur.execute(SQL)
            con.commit()
        except Exception as ex:
            print(ex)
            con.rollback()
            raise ex
        finally:
            con.close()

    def delete_user(self) -> bool:
        """Deletes `self` from database. Returns true if successfull."""
        con, cur = helpers.connect_to_db()

        # Delete user records from databases.
        try:
            SQL = "DELETE FROM users WHERE id='{}'".format(self.userid)
            cur.execute(SQL)
            con.commit()

            SQL = """
            UPDATE reservations 
            SET status='DELETED ACCOUNT' 
            WHERE customer_id={}""".format(
                self.userid
            )
            cur.execute(SQL)
            con.commit()

            SQL = """
            DELETE FROM messages
            WHERE to_id={0} OR from_id={1};""".format(
                self.userid, self.userid
            )

            cur.execute(SQL)
            con.commit()

        except Exception as ex:
            con.rollback()
            raise ex

    def get_all_users() -> list():
        """Returns all users in database"""
        cur, con = helpers.connect_to_db()
        sql = """
            SELECT * FROM users WHERE 1=1;
        """
        try:
            rows = list(cur.execute(sql).fetchall())
            return rows
        except Exception as ex:
            current_app.log_exception(ex)
            raise ex
        finally:
            con.close()

    def clone(self) -> "User":
        """Returns self. Useful for changing specific data when updating database."""
        return self
