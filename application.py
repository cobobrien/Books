import os
import sys
from _pydecimal import Decimal

import flask
import json
import requests
from flask import Flask, session, render_template, request, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.debug import console

app = Flask(__name__)

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(
    "postgres://vhjyekzkrkegue:a9cc9f23a4fdb74786ed0c0fbc80c48b17ff43dad73ef5b368dc3bb54900c3b8@ec2-54-228-243-29.eu-west-1.compute.amazonaws.com:5432/d7ib28jtsc6inn")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index(message=None):
    if session.get("login") is None:
        return render_template("login.html", message="Please log in to continue")

    search = ""
    if (flask.request.method == 'POST' and message == None):
        try:
            search = request.form.get("search")
            search = search.lower()
        except ValueError:
            return render_template("error.html", message="Invalid book number.")

    books = db.execute(
        "SELECT * FROM books WHERE isbn LIKE :isbn OR LOWER(author) LIKE :author OR LOWER(title) LIKE :title",
        {"isbn": "%" + search + "%", "author": "%" + search + "%", "title": "%" + search + "%"}).fetchall()
    return render_template("index.html", books=books, message=message)


@app.route("/books/<string:isbn>")
def book(isbn):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    reviews = db.execute(
        "SELECT user_id, review,rating FROM reviews JOIN books ON books.isbn = reviews.book WHERE isbn = :isbn",
        {"isbn": isbn}).fetchall()
    users = db.execute(
        "SELECT id,first_name,last_name FROM users WHERE id IN(SELECT user_id FROM reviews JOIN books ON books.isbn = reviews.book WHERE isbn = :isbn)",
        {"isbn": isbn}).fetchall()
    hasReviewed = db.execute("SELECT id FROM reviews WHERE book = :isbn AND user_id = :user_id",
                             {"isbn": isbn, "user_id": int(session.get("user_id")[0])}).fetchone()
    print(f"Reviews: {reviews}")
    print(f"Users: {users}")
    print(f"hasReviewed: {hasReviewed}")
    review_user = list(zip(reviews, users))
    if book is None:
        return render_template("error.html", message="No such book.")
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "ykoHXNthhLxDRx4lAkKPnw", "isbns": isbn})
    grReviews = res.json()
    averageRatings = grReviews['books'][0]['average_rating']
    ratingsCount = grReviews['books'][0]['work_ratings_count']
    return render_template("book.html", book=book, review_user=review_user, hasReviewed=hasReviewed,
                           averageRatings=averageRatings, ratingsCount=ratingsCount)


@app.route("/review", methods=["POST"])
def review():
    try:
        book_id = request.args.get("book")
        review_text = request.form.get("subject")
        rating = int(request.form["rating-input"])
        user_id = int(session.get("user_id")[0])
    except ValueError:
        return render_template("error.html", message="There was and error trying to process your review")
    db.execute(
        "INSERT INTO reviews (review, rating, book, user_id) VALUES (:review, :rating, :book, :user_id)",
        {"review": review_text, "rating": rating, "book": book_id, "user_id": user_id})
    db.commit()
    return book(book_id)


@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        user_name = request.form.get("username")
        password = request.form.get("password")
    except ValueError:
        return render_template("error.html", message="There was and error trying to log you in")
    user_id = db.execute("SELECT id FROM users WHERE user_name = :user_name AND password = :password",
                         {"user_name": user_name, "password": password}).fetchone()
    if (user_id):
        session["user_id"] = user_id
        session["login"] = True
        return index("Login Successful")
    elif (user_name != None and password != None):
        return render_template("login.html", message="Username or Password incorrect")
    else:
        return render_template("login.html", message=None)


@app.route("/register", methods=["POST", "GET"])
def register():
    if flask.request.method == 'POST':
        try:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            user_name = request.form.get("username")
            password = request.form.get("password")
        except ValueError:
            return render_template("error.html", message="There was and error trying to register you")
        db.execute(
            "INSERT INTO users (first_name, last_name, user_name, password) VALUES (:first_name, :last_name, :user_name, :password)",
            {"first_name": first_name, "last_name": last_name, "user_name": user_name, "password": password})
        db.commit()
        return render_template("login.html", message="Please log in to continue")
    else:
        return render_template("register.html")


@app.route("/logout", methods=["GET"])
def logout():
    session["login"] = False
    return render_template("logout.html")


@app.route("/api/<string:isbn>", methods=["GET"])
def bookapi(isbn):
    try:
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        reviews = db.execute("SELECT COUNT(*) as count, AVG(rating) as avg FROM reviews JOIN books ON books.isbn = reviews.book WHERE book = :isbn",
            {"isbn": isbn}).fetchall()
    except ValueError:
        return render_template("error.html", message="An error has occurred")
    if book is None:
        abort(404)
    avg_review = round(float(reviews[0][1]), 2)
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": reviews[0][0],
        "average_score": avg_review
    })

