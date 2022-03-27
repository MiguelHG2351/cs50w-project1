import os

from flask import Flask, jsonify, render_template, request, redirect, make_response
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime
import requests

# custom orm
from lib.db import SQL_Lib
from services.books import get_all_books, find_books
from services.users import find_user, create_user, find_one_user

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

@app.route("/books/<book_isbn>")
@isAutenticated
def books_info(book_isbn):
    get_host_and_protocol = request.url_root
    get_some_books = requests.get(f'{get_host_and_protocol}/api/v1/find_books?filterBy=10&isbn={book_isbn}').json()

    return render_template("books.html", book=get_some_books)


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

        payload = {
            "username": username,
            "lastname": lastname,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "nbf": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, key=os.getenv(
            'JWT_SECRET_KEY'), algorithm='HS256')

        _create_user = create_user(username, lastname, email, generate_password_hash(password))
        if(not _create_user['success']):
            print(_create_user['message'])
            return jsonify({"success": False, "message": "Can't create user"})

        print(_create_user)
        response = make_response(jsonify({
            'success': True,
        }))
        response.set_cookie('token', token)
        return response
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
        print(get_user)
        if(get_user['success'] and check_password_hash((get_user['data'])[3], password)):
            response = make_response(jsonify({
                'success': True,
            }))
            token = jwt.encode({
                "email": email,
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
    print('books')

    print(len(books["data"]))
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

    return jsonify(books_array)

@app.errorhandler(404)
def not_found(error):
    if request.cookies.get('token'):
        return redirect('/')
    return redirect('/login')
