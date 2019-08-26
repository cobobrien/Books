import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://vhjyekzkrkegue:a9cc9f23a4fdb74786ed0c0fbc80c48b17ff43dad73ef5b368dc3bb54900c3b8@ec2-54-228-243-29.eu-west-1.compute.amazonaws.com:5432/d7ib28jtsc6inn")

db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} by {author}")
    db.commit()

if __name__ == "__main__":
    main()
