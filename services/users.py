from lib.db import SQL_Lib

db = SQL_Lib()

table = 'users'

def create_user(username, lastname, email, password):
    return db.create(table, {"username": username, "lastname": lastname, "email": email, "password": password})

def find_user(email):
    return db.find(table, "email", email, 2)

def find_one_user(email):
    return db.find_by_id(table, email, "email")

def find_one_id(user_id):
    return db.find_by_id(table, user_id)
