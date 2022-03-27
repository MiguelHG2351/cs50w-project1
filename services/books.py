# from lib.db import find, find_by_id, get_all
from lib.db import SQL_Lib

db = SQL_Lib()
def get_all_books(limit):
    return db.get_all("books", limit)

def find_books(field, value, limit):
    return db.find("books", field, value, limit)

def find_isbn(isbn):
    return db.find_by_id("books", isbn, "isbn")
