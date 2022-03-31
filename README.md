# Portfolio Prüfung Verteilte Systeme

## Einführung
Die im Kurs "Verteilte Systeme" gestellte Portfolioprüfung besteht aus drei verschiedenen auf einander aufbauenden Teilbereiche. Gemeinsam witmen sich diese Teilbereiche der Entwicklung, Auslieferung und Dokumentation eines Microservices zum Ablegen und Abfragen von Buch-titeln , -autoren, -ISBNs und -sprachen in einer NoSQL-Datenbank. Die Entwicklung und Auslieferung der Datenbank ist kein Bestandteil der Portfolioprüfung, weshalb im Rahmen dieser Arbeit eine CouchDB Datenbank nach den, im Anhang der Aufgabenstellung, enthaltenden Informationen eingesetzt wird.

## Library Microservice

Im ersten Teil der Portfolioprüfung wird der Microservice entwickelt. Der Service soll über vier API Endpunkte verfügen, welche auf verschiedene Weisenmit der verbundnen Datenbank kommunizieren.  
### **Get all Books**
Über den ersten Endpunkt sollen alle Bücher, welche sich in der Datenbank befinden, mittels einer HTTP-GET Anfrage an die Route "api/v1/getall", im JSON Format an den Benutzer zurückgegeben werden. Ergebnisse der Anfrage können demnach die vollständige Liste aller Bücher, oder ein Hinweis auf eine leere Datenbank sein.

***Call Example***  
curl -X GET 'http://localhost:8080/api/v1/getall'

***Result Examples***
<pre>
HTTP 200
{
   "0": {  
        "AUTHOR": "Adler-Olsen, Jussi",  
        "TITLE": "Natrium Chlorid",  
        "LANGUAGE": "de",  
        "ISBN": "978-3-423-28280-2"  
        },  
    1: {...}
}
OR
HTTP 200
{"INFO": "The book listing is empty"}
</pre>

### **Get Book by ISDN**
Mittels zweitem API Endpunkt soll in der Datenbank nach einem Buch mit gegebener ISBN Nummer gesucht werden. Die ISBN bildet dabei den Query-Parameter der HTTP-GET Anfrage and die Route "/api/v1/get_isbn". Die Ausgabe dieser Anfrage kann dabei erfolgreich sein, indem das gesuchte Buch zurückgegeben wird, oder ein Hinweis übertragen wird, dass kein Buch mit der angegebenen ISBN in der Datenbank enthalten ist. Die Anfrage verläuft nicht erfolgreich, wenn der Hinweis ausgegeben wird, dass nach einer ungültige ISBN gesucht wird.  
***Call Example:***  
<pre>
curl -X GET 'http://localhost:8080/api/v1/get_isbn?isbn=978-3-423-28280-2'
</pre>
***Result Examples***
<pre>
HTTP 200
{
"AUTHOR": "Adler-Olsen, Jussi",
"TITLE": "Natrium Chlorid",
"LANGUAGE": "de",
"ISBN": "978-3-423-28280-2"
}
OR
HTTP 202
{ "INFO": "The book with the isbn number 978-3-423-28280-2 is not in our book listing"}
OR
HTTP 400
{"detail": "Invalid ISBN!"}
</pre>

### **Create Book Entry**
Der dritte Endpunkt der Library Microservice API dient der Erzeugung eines Buch-Eintrages in die verbundene CouchDB Datenbank. Die HTTP-PUT Anfrage and die Route "/api/v1/create" verlangt dabei nach einem übertragenem Body, in welchem die Buchinformationen im JSON Format vorliegen. Bei dieser Anfrage erfolgen zwei Prüfungen. Zuerst wird die ISBN des zu erstellenden Eintrags auf ihre Gültigkeit getestet.  Anschließend wird der übermittelte Eintrag mit den in der Datenbank vorliegenden Einträgen abgeglichen, um Duplikate zu vermeiden. Je nach Erfolg oder Misserfolg der Prüfungen kann der Rückgabewert des Endpunktes auf die erfolgreiche Erstellung, einen bereits vorhandenen Eintrags, oder eine ungültige ISBN-Nummer hinweisen. 
***Call Example:***  
<pre>
curl -X 'PUT' 'http://localhost:8080/api/v1/create' -H 'accept: application/json' \
-H 'Content-Type: application/json' -d '{
"author": "Cavanagh, Steve",
"title": "Thirteen",
"lang": "de",
"isbn": "978-3-442-49215-2"}'
</pre>
***Result Examples***
<pre>
HTTP 200
{
  "SUCCESS": {
    "doc_id": "1f2480c0992584c170d8421385000be0", 
    "doc_rev": "1-eca4f6980e00ed11a02f19491820e4f3"
  }
}
OR
HTTP 400
{
  "detail": "Invalid ISBN!"
}
OR
HTTP 400
{
  "detail": "Book already present in library database"
}
</pre>

### **Health Endpoint**
Der Health Endpunkt gibt auf eine HTTP-GET Anfrage and die Route "/health" eine kurze Rückmeldung zur Verfügbarkeit des Microservices. So ist der Microservice erreichbar, wird an diesem Endpunkt ein JSON mit dem Key-Value Paar {"Status": "UP"} an den Anfragenden zurückgesendet. Wird diese Rückmeldung nicht empfangen, so ist der Mikroservice offensichtlich nicht erreichbar.
***Call Example:*** 
<pre>
curl -X GET 'http://localhost:8080/health'
</pre>
***Result Example***
<pre>
HTTP 400
{
"detail": "Invalid ISBN!"
}
</pre>