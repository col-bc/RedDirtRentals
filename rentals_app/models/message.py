from flask.globals import current_app
import rentals_app.helpers as helpers
from rentals_app.models.user import *

class Message():

    def __init__(self, from_user:User, to_user:User, subject:str, message: str, status:str = "New") -> None:
        self.from_user = from_user
        self.to_user = to_user
        self.subject = subject
        self.message = message
        self.status = status
    
    # Commits message contents to database
    def send_message(self) -> bool:
        con, cur = helpers.connect_to_db()
        sql = """
        INSERT INTO messages (
            from_id,
            to_id, 
            subject,
            message,
            status
        )
        VALUES (
            '{0}',
            '{1}',
            '{2}',
            '{3}',
            '{4}'
        );
        """.format(self.from_user, self.to_user, self.subject, self.message, self.status)

        try:
            cur.execute(sql)
            con.commit()
            return True
        except Exception as ex:
            con.rollback()
            raise ex
        finally:
            con.close()

    # Returns number of messages sent to User
    def check_num_messages(user:User) -> int:
        cur, con = helpers.connect_to_db()

        sql = """
        SELECT * FROM messages WHERE to_id = '{}';
        """.format(user.userid)

        try:
            messages = cur.execute(sql).fetchall()
            if not messages:
                return 0
            else:
                return len(messages)
        except Exception as ex:
            raise ex
        finally:
            con.close()

    # Returns number of new messages send to User
    def check_new_messages(user:User) -> int:
        cur, con = helpers.connect_to_db()

        sql = """
        SELECT * FROM messages WHERE to_id = '{}', status='New';
        """.format(user.userid)

        try:
            messages = cur.execute(sql).fetchall()
            if not messages:
                return 0
            else:
                return len(messages)
        except Exception as ex:
            raise ex
        finally:
            con.close()

    # Returns list of messages to provided user obj
    def get_messages(user:User) -> list():
        con, cur = helpers.connect_to_db();
        sql = """
            SELECT * FROM messages WHERE to_id='{}'
        """.format(user.userid)
        try:
            results = cur.execute(sql).fetchall()
            return list(results)
        except Exception as ex:
            current_app.log_exception(ex)
            raise ex
        finally:
            con.close()
            

