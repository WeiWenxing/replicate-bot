import shelve


class User:
    def __init__(self, id, token, points, cash):
        self.id = id
        self.token = token
        self.points = points
        self.cash = cash

    def __str__(self):
        return f"User(id={self.id}, token={self.token}, points={self.points}, cash={self.cash})"


class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def add_user(self, user):
        with shelve.open(self.db_file, flag='w', writeback=True) as db:
            db[user.id] = user

    def get_user(self, id):
        with shelve.open(self.db_file) as db:
            return db.get(id)

    def delete_user(self, id):
        with shelve.open(self.db_file, flag='w', writeback=True) as db:
            if id in db:
                del db[id]

    def update_user(self, user):
        with shelve.open(self.db_file, flag='w', writeback=True) as db:
            if user.id in db:
                db[user.id] = user
