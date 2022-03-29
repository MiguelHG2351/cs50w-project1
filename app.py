import os

from flask import Flask, jsonify, render_template, request, redirect, make_response
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime
import requests

# custom orm
from lib.db import SQL_Lib

# services
from services.books import get_all_books, find_books, find_isbn
from services.users import find_user, create_user, find_one_user
from services.opinion import uploadOpinion, get_opinion, get_all_opinions

# JWT
import jwt

from functools import wraps

# security with werkzeug
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Check for environment variable
if not os.getenv("URL_DATABASE"):
    raise RuntimeError("URL_DATABASE is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("URL_DATABASE"))
db = scoped_session(sessionmaker(bind=engine))
# set up database2
SQL_Lib()

def isAutenticated(f):
    @wraps(f)
    def decorateFn(*args, **kwargs):
        if request.cookies.get('token'):
            try:
                verify = jwt.decode(request.cookies.get('token'), os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
                return f(*args, **kwargs)
            except jwt.InvalidTokenError:
                return redirect('/register')
        else:
            return redirect('/register')
    return decorateFn

@app.route("/")
@isAutenticated
def index():
    return render_template("index.html")

@app.route("/books")
@isAutenticated
def books_fn():
    get_host_and_protocol = request.url_root
    try:
        get_some_books = requests.get(f'{get_host_and_protocol}/api/v1/get_books?limit=10')
    except Exception as e:
        print('K')

    return render_template("books.html", books=get_some_books.json())

@app.route("/books/<book_isbn>", methods=["GET", "POST"])
@isAutenticated
def books_info(book_isbn):
    if request.method == "POST":
        opinion = request.form.get("opinion")
        score = request.form.get("score")
        created_at_time = datetime.datetime.now()
        try:
            user_id = jwt.decode(request.cookies.get('token'), os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])['id']
            find_opinion = get_opinion(user_id, book_isbn)
            if find_opinion['data'] is None or str(find_opinion['data'][3]) != book_isbn and find_opinion['data'][2] != user_id:
                    si = uploadOpinion(user_id, book_isbn, opinion, score, created_at_time)
                    return jsonify({"success": True, "message": "Opinion uploaded"})
            else:
                return jsonify({"success": False, "message": "You already have an opinion"}), 400
        except Exception as e:
            return redirect('/books')
        
    get_host_and_protocol = request.url_root
    _get_all_opinions = get_all_opinions(book_isbn)
    print( _get_all_opinions)
    opinions_array = []
    for id, user_score, user_id, book_id, user_comment, created_at in _get_all_opinions['data']:
        opinions_array.append({
            "user_score": user_score,
            "user_id": user_id,
            "book_id": book_id,
            "user_comment": user_comment,
            "created_at": created_at
        })
    print(opinions_array)
    get_some_books = requests.get(f'{get_host_and_protocol}/api/v1/get_book?isbn={book_isbn}').json()


    return render_template("book.html", book=get_some_books, opinions=opinions_array)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")

        if(username == "" or lastname == "" or email == "" or password == ""):
            return jsonify({"success": False, "message": "Please fill in all the fields"})

        _find_user = find_user(email)
        if(not _find_user['success']):
            return jsonify({"success": False, "message": "Unexpected Error"})
        if(len(_find_user['data']) > 0):
            return jsonify({"success": False, "message": "Account already exists"})

        _create_user = create_user(username, lastname, email, generate_password_hash(password))
        
        if(not _create_user['success']):
            return jsonify({"success": False, "message": "Can't create user"})

        return jsonify({
            'success': True,
        })
        # except Exception as e:
        #     print(e)
        #     db.rollback()
        #     flash("Something went wrong")
        #     return jsonify({"success": False, "message": "Something went wrong"})

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if(email == "" or password == ""):
            return jsonify({"success": False, "message": "Please fill in all the fields"})

        get_user = find_one_user(email)

        if(get_user['success'] and check_password_hash((get_user['data'])[3], password)):
            response = make_response(jsonify({
                'success': True,
            }))
            token = jwt.encode({
                "email": email,
                'id': (get_user['data'])[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                "nbf": datetime.datetime.utcnow()
            }, key=os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

            response.set_cookie('token', token)
            return response
        else:
            return jsonify({"success": False, "message": "Wrong credentials"})

    response = make_response(render_template("login.html"))

    return response

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('token', '', expires=0)
    return response

# API
@app.route('/api/v1/get_books', methods=['GET'])
def get_books():
    limit = request.args.get('limit') or 10 # Se pasa a int por que el parametro viene como string
    if type(limit) != int:
        try:
            limit = int(limit)
        except:
            return jsonify({"success": False, "message": "Limit must be an integer"})
    books = get_all_books(limit) # Busca todos los libros

    if(books['success']):
        books_array = []
        for isbn, title, author, year in books['data']:
            books_array.append({
                "isbn": isbn,
                "title": title,
                "author": author,
                "year": year
            })
        return jsonify(books_array)
    else:
        return jsonify({"success": False, "message": "Something went wrong"})

@app.route('/api/v1/get_book', methods=['GET'])
def get_book():
    isbn = request.args.get('isbn')
    if(isbn == None):
        return jsonify({"success": False, "message": "Please provide an ISBN"})
    book = find_isbn(isbn)
    get_google_book_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}').json()['items'][0]
    
    if(book['success']):
        data = book['data']
        return jsonify({
            "isbn": data['isbn'],
            "title": data['title'],
            "author": data['author'],
            "year": data['year'],
            "review_count": get_google_book_info['volumeInfo']['ratingsCount'],
            "average_score": get_google_book_info['volumeInfo']['averageRating'],
            'picture': get_google_book_info['volumeInfo']['imageLinks']['thumbnail'],
        })
    else:
        return jsonify({"success": False, "message": "Something went wrong"})

@app.route('/api/v1/find_books', methods=['GET'])
def find_books_():
    available_filters = ('isbn', 'title', 'author')
    limit = 10
    filterBy = request.args.get('filterBy')

    if filterBy not in available_filters:
        return jsonify({"success": False, "message": "Filter not available"})
    
    books = find_books(filterBy, request.args.get('value'), limit) # Busca todos los libros por cierto campo
    books_array = []

    for isbn, title, author, year in books['data']:
        books_array.append({
            "isbn": isbn,
            "title": title,
            "author": author,
            "year": year
        })

    return jsonify({
        "success": True,
        "data": books_array
    })

@app.errorhandler(404)
def not_found(error):
    if request.cookies.get('token'):
        return redirect('/')
    return redirect('/login')
