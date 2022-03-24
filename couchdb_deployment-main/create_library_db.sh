#!/bin/bash

echo "CouchDB Adresse (default: localhost)"
read HOST
HOST="${HOST:=localhost}"

echo "CouchDB Port (default: 5984)"
read PORT
PORT="${PORT:=5984}"

echo "CouchDB User (default: admin)"
read USER
USER="${USER:=admin}"

echo "CouchDB Passwort (default: student)"
read PASSWORD
PASSWORD="${PASSWORD:=student}"

CDB="$USER:$PASSWORD@$HOST:$PORT"

echo "Ziel-URL: $CDB"
echo "========================================"
echo ""


# Datenbank library anlegen:
curl -X PUT http://$CDB/library

# 5 Datensätze schreiben:
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d '{"author": "King, Stephen", "title": "Es", "lang": "de", "isbn": "978-3-453-43577-3"}' 
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d '{"author": "King, Stephen", "title": "Friedhof der Kuscheltiere", "lang": "de", "isbn": "978-3-453-44160-6"}'
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d '{"author": "Irving, John", "title": "The Hotel New Hampshire", "lang": "en", "isbn": "978-0-345-40047-5"}'
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d '{"author": "Melandri, Francesca", "title": "Über Meereshöhe", "lang": "de", "isbn": "978-3-8031-2812-6"}'
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d '{"author": "Highsmith,Patricia", "title": "The Talented Mr. Ripley", "lang": "en", "isbn": "978-3-15-009145-6"}'

# View Document anlegen:
curl -H 'Content-Type: application/json' -X POST http://$CDB/library -d \
'{
 "_id": "_design/books",
 "views": {
     "byAuthor": {
         "map": "function (document) { emit(document.author, document); }"
     },
     "byTitle": {
         "map": "function (document) { emit(document.title, document); }"
     },
     "byLanguage": {
         "map": "function (document) { emit(document.lang, document); }"
     },
     "byISBN": {
         "map": "function (document) { emit(document.isbn, document); }"
     }
 },
 "language": "javascript"
}'
