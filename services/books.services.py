# from lib.db import find, find_by_id, get_all
from lib.db import SQL_Lib

db = SQL_Lib()
def getAllBooks():
    return db.get_all("books")

def findBooks(field, value, limit):
    return db.find("books", field, value, limit)

def find_isbn(isbn):
    return db.find_by_id("books", isbn, "isbn")
