from http import HTTPStatus
from sre_constants import SUCCESS
from unittest import result
import requests
import re
import json
from flask import Flask, request
import couchdb

app = Flask(__name__)

@app.route("/")
def title_page():
    '''Route returns a welcoming page explaining the basic API endpoints'''
    if database_connection:
        return  """ <h1>Hello on my booklibrary API</h1>
                    <h2>This API has following endpoints</h2>
                    <p><b>Get a list of all available books</b></p>
                    <p>Operation: GET, Path: /api/v1/getall call e.g. curl -X GET 'http://localhost:8080/api/v1/getall'</p>
                    <p><b>Get a book by its isbn number</b></p>
                    <p>Operation: GET, Path: /api/v1/get_isbn Query-Parameter: isbn (string) call e.g. curl -X GET 'http://localhost:8080/api/v1/get_isbn?isbn=978-3-453-43577-4'</p> 
                    <p><b>Creating a Book given a json with information about author, title, isbn, language</b></p>
                    <p>Operation: PUT, Path: /api/v1/create Request body: {"author": "string", "title": "string", "lang":"string", "isbn": "string"}</p>
                    <p>Call e.g. curl -X 'PUT' 'http://localhost:8080/api/v1/create' -H 'accept: application/json' \
                        -H 'Content-Type: application/json' -d '{
                        "author": "Cavanagh, Steve",
                        "title": "Thirteen",
                        "lang": "de",
                        "isbn": "978-3-442-49215-2"}'</p>
                    <p><b>Testing the availability from the microservice</b></p>
                    <p>Operation: GET, Path: /health Result: {"status": "UP"}</p>
                """
    else: return """<h1>Hello on my booklibrary API</h1>
                    <h2>The API is currently not available due to missing database</h2>"""


@app.route("/api/v1/getall", methods=["GET"])
def get_all():
    '''Returns all Books from the Database in a JSON format'''
    if database_connection:
        result_dict = {}
        count = 0
        for id in db:
            if len(id) > 14:
                doc = db[id]
                result_dict.update({str(count)+":": {"AUTHOR": doc["author"], "TITLE": doc["title"], "LANGUAGE": doc["lang"], "ISBN": doc["isbn"]}})
                count += 1
        if len(result_dict) == 0:
            return {"INFO": "The book listing is empty"}, 200
        return result_dict, 200
    else: return {"ERROR":"Connection Error, Database couldnt be reached"}, 500

@app.route("/api/v1/get_isbn", methods=["GET"])
def get_isbn_query():
    '''Takes an isbn number as a query parameter. Returns the other bookinformation to that ISBN if available'''
    if database_connection:
        args = request.args.to_dict()
        isbn = args.get("isbn")
        if check(isbn):
            result_dict = {}
            count = 0
            for id in db:
                if len(id) > 14:
                    doc = db[id]
                    if doc["isbn"] == isbn:
                        result_dict.update({"Book "+ str(count)+":": {"AUTHOR": doc["author"], "TITLE": doc["title"], "LANGUAGE": doc["lang"], "ISBN": doc["isbn"]}})
                        return result_dict, 200
            return {"INFO": "The book with the isbn number "+ isbn+ " is not in our book listing"}, 202
        else: return {"detail": "Invalid ISBN!"}, 400
    else: return {"ERROR":"Connection Error, Database couldnt be reached"}

@app.route("/api/v1/create", methods = ['PUT'])
def create_book():
    '''Takes a body with a JSON string within. Returns a success alert, if a database entry was created'''
    if database_connection:
        creating_book = json.loads(request.data.decode('utf-8'))
        if check(creating_book.get("isbn")):
            if existing_book(creating_book.get("isbn")):
                db.save(creating_book)
                print(creating_book)
                response = {"SUCCESS": {"doc_id": creating_book.get("_id"), "doc_rev":creating_book.get("_rev")}}
                return response,200
            else: return {"detail": "Book already present in library database"}, 400
        else: return {"detail": "Invalid ISBN!"}, 400
    else: return {"ERROR":"Connection Error, Database couldnt be reached"}, 500

@app.route("/health", methods = ['GET'])
def check_health():
    '''Returns a JSON String, demonstrating that the microservice is available'''
    if database_connection:
        return {"status": "UP"},200
    else: return {"status": "UP / No Database"}

# Function copied from https://rosettacode.org/wiki/ISBN13_check_digit#Python (30.03.2022)
def check(n):
    '''Takes an ISBN number. Returns True or False wheter the ISBN is valid'''
    n = n.replace('-','').replace(' ', '')
    if len(n) != 13:
        return False
    product = (sum(int(ch) for ch in n[::2]) 
               + sum(int(ch) * 3 for ch in n[1::2]))
    return product % 10 == 0

def existing_book(isbn):
    '''Calls the get_isbn endpoint, to check if an entry exists with the given ISBN'''
    url = "http://"+app.config["SERVER_NAME"]+ "/api/v1/get_isbn?isbn="+str(isbn)
    result = requests.head(url)
    return (result.status_code == 202)

def build_connection():
    couch = couchdb.Server(app.config["COUCHDB_SERVER"])
    db = couch['library']
    database_connection = True
    return db, database_connection


if __name__ == '__main__':
    app.config.from_object("api_config.DevelopmentConfig")
    database_connection = False
    try:
        couch = couchdb.Server(app.config["COUCHDB_SERVER"])
        db = couch['library']
        database_connection = True
        app.run()
    except ConnectionError:
        error_msg = "ERROR: Connection Error, Database couldnt be reached"
        print(error_msg)
    app.run()
    
    
