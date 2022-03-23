import os

from flask import Flask, jsonify, session, render_template, request, flash, redirect, make_response
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime

# JWT
import jwt

from functools import wraps

# security with werkzeug
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")

        if(username == "" or lastname == "" or email == "" or password == ""):
            return jsonify({"success": False, "message": "Please fill in all the fields"})
        if(db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount != 0):
            return jsonify({"success": False, "message": "Username already exists"})

        payload = {
            "username": username,
            "lastname": lastname,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "nbf": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, key=os.getenv(
            'JWT_SECRET_KEY'), algorithm='HS256')
        try:
            create_user = db.execute("INSERT INTO users (username, lastname, email, password) VALUES (:username, :lastname, :email, :password)", {
                "username": username, "lastname": lastname, "email": email, "password": generate_password_hash(password)})
            db.commit()
            flash("User created successfully")

            print(create_user)
            response = make_response(jsonify({
                'success': True,
            }))
            response.set_cookie('token', token)
            return response
        except Exception as e:
            print(e)
            db.rollback()
            flash("Something went wrong")
            return redirect("/register")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if(email == "" or password == ""):
            flash("Please fill in all the fields")
            return redirect("/register")
        user = db.execute("SELECT * FROM users WHERE email = :email", {"email": email})
        if(user.rowcount != 0 and check_password_hash((user.fetchone())[3], password)):
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


    response = make_response(render_template("login.html"))

    return response
