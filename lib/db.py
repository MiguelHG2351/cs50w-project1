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

    def get_all(self, table, limit=10):
        try:
            query = f"SELECT * FROM {table} {'limit :_limit' if limit > 0 else '' }"
            print(query)
            data = db.execute(query, {'_limit': limit}).fetchall()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "message": 'Efe'}

    def find(self, table, field, value, limit):
        try:
            data = db.execute(f"SELECT * FROM {table} WHERE {field} like :value LIMIT :limit", {"value": f'%{value}%', "limit": limit}).fetchall()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "message": e}
    
    def find_all(self, table, field, value, limit):
        try:
            data = db.execute(f"SELECT * FROM {table} WHERE {field} = :value LIMIT :limit", {"value": value, "limit": limit}).fetchall()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "message": e}

    def find_by_id(self, table, value,  field='id'):
        try:
            data = db.execute(f"SELECT * FROM {table} WHERE {field} = :value", {"value": value}).fetchone()
            print(data)
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'message': e}
        
    def find_one(self, table, dict_data, operation=''):
        where_condition = ''
        for key, value in dict_data.items():
            where_condition += f" {key} = '{value}' {operation} "
        where_condition = where_condition[:-len(operation) - 1]
        print(where_condition)
        try:
            print(f"SELECT * FROM {table} WHERE {where_condition}")
            data = db.execute(f"SELECT * FROM {table} WHERE {where_condition}").fetchone()
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'message': e}

    def create(self, table, data_dict):
        field = ', '.join(str(x) for x in data_dict.keys())
        value = ', '.join("'"+str(x)+"'" for x in data_dict.values())
        try:
            data = db.execute(f"INSERT INTO {table} ({field}) VALUES ({value})")
            db.commit()
            # return id
            return {'success': True, 'data': data.lastrowid}
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': e}

    def update(self, table, field, value):
        try:
            data = db.execute(f"UPDATE {table} SET {field} = {value}")
            db.commit()
            return {'success': True, 'data': data}
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': e}