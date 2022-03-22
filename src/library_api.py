from flask import Flask, url_for, request

app = Flask(__name__)

@app.route("/")
def title_page():
    return '<a href = ' + url_for("get_isbn", isbn= 1337) + '>Such nach 1337</a>' # linking on the get_isbn route

@app.route("/api/v1/getall", methods=["GET"])
def get_all():
    return {'author':'Leon',
                    'title': 'How to API'}

@app.route("/api/v1/get_isbn/<string:isbn>", methods=["GET"]) # including variables in the URL
def get_isbn(isbn):
    return "<p>Are you looking for " + str(isbn) + " "+ str(type(isbn))+"? </p>"

@app.route("/api/v1/create", methods = ['PUT'])
def create_book():
    if request.method == "PUT":
        isbn = request.body

if __name__ == '__main__':
    app.run(port=3000, debug=True)