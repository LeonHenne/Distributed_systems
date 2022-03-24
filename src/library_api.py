from http import HTTPStatus
from unittest import result
from flask import Flask, url_for, request, jsonify
import couchdb

app = Flask(__name__)

@app.route("/")
def title_page():
    return  """ <h1>Hello on my booklibrary API</h1>
                <h2>This API has following endpoints</h2>
                <p>"/api/v1/getall" will get you all of the available books</p>
                <p>"/api/v1/get_isbn/isbn" will get you a book by its isbn number</p>
                <p>"/api/v1/create" will create a book in the couchdb Database</p>
                <p>"/health" will test the availability from the microservice</p>
            """

@app.route("/api/v1/getall", methods=["GET"])
def get_all():
    result_dict = {}
    count = 0
    for id in db:
        if len(id) > 14:
            doc = db[id]
            result_dict.update({"Book "+ str(count)+":": {"AUTHOR": doc["author"], "TITLE": doc["title"], "LANGUAGE": doc["lang"], "ISBN": doc["isbn"]}})
            count += 1
    if len(result_dict) == 0:
        return {"INFO": "The book listing is empty"} 
    return result_dict

@app.route("/api/v1/get_isbn/<string:isbn>", methods=["GET"])
def get_isbn(isbn):
    result_dict = {}
    count = 0
    for id in db:
        if len(id) > 14:
            doc = db[id]
            if doc["isbn"] == isbn:
                result_dict.update({"Book "+ str(count)+":": {"AUTHOR": doc["author"], "TITLE": doc["title"], "LANGUAGE": doc["lang"], "ISBN": doc["isbn"]}})
            else:
                result_dict.update({"INFO": "The book with the isbn number "+ isbn+ " is not in our book listing"})
    return result_dict

@app.route("/api/v1/create", methods = ['PUT'])
def create_book():
    if request.method == "PUT":
        body = request.body
        return body
        #doc_id, doc_rev = db.save(body)
        #doc_id, doc_rev = db.save({'type': 'Person', 'name': 'John Doe'})

@app.route("/health", methods = ['GET'])
def check_health():
    return {"status": "UP"}


if __name__ == '__main__':
    couch = couchdb.Server("http://admin:student@localhost:5984/")
    db = couch['library']
    app.run(port=3000, debug=True)
