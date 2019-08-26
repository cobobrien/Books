# Books
Book review Flask application - Integrated with Goodeads API and an exposed REST endpoint

## Features

* Postgres Backend
* Challenge here was not to use ORM for the server-database communication. Just raw SQL
* Also a challenge was in not using JavaScript on the frontend. Just pure HTML and CSS.
* Another challenge was in not using OOTB login and registration packages.
* Integrated with Goodreads API to pull review data from Goodreads web service.
* Exposed endpoint at /api/<isbn> that can be consumed by other web services. GET requests will get a JSON response of data from reviews left on this website.





