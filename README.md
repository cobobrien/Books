# Books
Book review Flask application - Integrated with Goodeads API and an exposed REST endpoint

###### Features

* Postgres Backend
* Challenge here was not to use ORM for the server-database communication. Just raw SQL
* Also a challenge was in not using JavaScript on the frontend. Just pure HTML and CSS.
* Integrated with Goodreads API to pull review data from Goodreads web service.
* Exposed endpoint at /api/<isbn>. GET requests will get a JSON response of data from reviews left on this website.
  
  `{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}`




