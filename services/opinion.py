from lib.db import SQL_Lib

db = SQL_Lib()

table = 'user_and_books'

def uploadOpinion(user_id, isbn, opinion, score, created_at):
    return db.create(table, {'user_id': user_id, 'book_id': isbn, 'user_comment': opinion, 'user_score': score, "created_at": created_at})

def get_opinion(user_id, book_id):
    return db.find_one(table, {
        "user_id": user_id,
        "book_id": book_id
    }, 'AND')

def get_all_opinions(isbn):
    return db.find_all(table, 'book_id', isbn, 100)
