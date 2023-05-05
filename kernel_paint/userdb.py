import shelve


def insert(dbname, id, token, points, cash):
    with shelve.open(dbname, flag='w', writeback=True) as s:
        s[id] = {'token': token, 'points': points, 'cash': cash}


def update(dbname, id, token=None, points=None, cash=None):
    with shelve.open(dbname, flag='w', writeback=True) as s:
        if token is not None:
            # s[id]['token'] = token
            s[id].update({'token': token})
        if points is not None:
            # s[id]['points'] = points
            s[id].update({'points': points})
        if cash is not None:
            # s[id]['cash'] = cash
            s[id].update({'cash': cash})


def delete(dbname, id):
    with shelve.open(dbname, flag='w', writeback=True) as s:
        del s[id]


def lookup(dbname, id):
    with shelve.open(dbname) as s:
        user_info = s.get(id)
    return user_info

