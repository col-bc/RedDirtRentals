import rentals_app.helpers

class User:

    def __init__(self, username,
        password,
        group,
        token=None,
        flags=None):
        self.username = username
        self.password = password
        self.group = group
        self.token = token
        self.flags = flags
