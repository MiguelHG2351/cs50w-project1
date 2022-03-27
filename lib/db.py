import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("URL_DATABASE"))
db = scoped_session(sessionmaker(bind=engine))

class SQL_Lib():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    
    def __init__(self):
        self.engine = create_engine(os.getenv("URL_DATABASE"))
        self.db = scoped_session(sessionmaker(bind=self.engine))

    def get_all(table):
        return db.execute(f"SELECT * FROM {table}").fetchall()

    def find(table, field, value, limit):
        return db.execute(f"SELECT * FROM {table} WHERE {field} like :value LIMIT :limit", {"value": f'%{value}%', "limit": limit}).fetchall()

    def find_by_id(table, value,  field='id'):
        return db.execute(f"SELECT * FROM {table} WHERE {field} = :value", {"value": value}).fetchone()

    def create(table, fields, values):
        db.execute(f"INSERT INTO {table} ({fields}) VALUES ({values})")
        db.commit()

    def update(table, field, value):
        db.execute(f"UPDATE {table} SET {field} = {value}")
        db.commit()