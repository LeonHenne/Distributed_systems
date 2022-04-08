# Portfolio Prüfung Verteilte Systeme

## Einführung
Die im Kurs "Verteilte Systeme" gestellte Portfolioprüfung besteht aus drei verschiedenen auf einander aufbauenden Teilbereiche. Gemeinsam witmen sich diese Teilbereiche der Entwicklung, Auslieferung und Dokumentation eines Microservices zum Ablegen und Abfragen von Buch-titeln , -autoren, -ISBNs und -sprachen in einer NoSQL-Datenbank. Die Entwicklung und Auslieferung der Datenbank ist kein Bestandteil der Portfolioprüfung, weshalb im Rahmen dieser Arbeit eine CouchDB Datenbank nach den, im Anhang der Aufgabenstellung, enthaltenden Informationen eingesetzt wird.

## Library Microservice

Im ersten Teil der Portfolioprüfung wird der Microservice entwickelt. Der Service soll über vier API Endpunkte verfügen, welche auf verschiedene Weisenmit der verbundnen Datenbank kommunizieren.  
### **Get all Books**
Über den ersten Endpunkt sollen alle Bücher, welche sich in der Datenbank befinden, mittels einer HTTP-GET Anfrage an die Route "api/v1/getall", im JSON Format an den Benutzer zurückgegeben werden. Ergebnisse der Anfrage können demnach die vollständige Liste aller Bücher, oder ein Hinweis auf eine leere Datenbank sein.

***Call Example***  
curl -X GET 'http://0.0.0.0:8080/api/v1/getall'

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
curl -X GET 'http://0.0.0.0:8080/api/v1/get_isbn?isbn=978-3-423-28280-2'
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
curl -X 'PUT' 'http://0.0.0.0:8080/api/v1/create' -H 'accept: application/json' \
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
curl -X GET 'http://0.0.0.0:8080/health'
</pre>
***Result Example***
<pre>
HTTP 200
{
  "status": "UP"
}
</pre>


## Docker Deployment
Nach der Entwicklung des Microservices behandelt der folgende Teil die Auslieferung der Anwendung über einen Container. Ein Container stellt eine auf betriebssystemebene virtualisierte Umgebung zur Verfügung.
Der Microservice, sowie die benötigte CouchDB müssen dazu in jeweils einem Container innerhalb eines gemeinsamen Netzwerkes zur Verfügung gestellt werden. Die Erstellung eines Containers startet mit dem Schreiben eines Dockerfiles. In dieser Datei wird zunächst das grundlegende virtualisierte Betriebssystem als  Basisimage angegeben. Im Weiteren werden Anweisungen beschrieben zum Freigeben von Ports, installieren von Paketen sowie Kopieren und Ausführen der benötigten Dateien. Insgesamt baut sich das Dockerfile aus folgenden Hauptkomponenten zusammen:  
<pre>
FROM python:3.8-slim # loading the base image

EXPOSE 8080 # exposing the desired port which will be mapped

RUN python -m pip install -r requirements.txt # Install pip requirements

CMD ["python", "src/library_api.py"] # starts a python session and executes the sourcefile 
</pre>  

***Starten des CouchDB Containers:***  
<pre>docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=student \  
--network lib-network --network-alias couchdb \  
-v "lokaler Pfad zum Repository"/couchdb/data:/opt/couchdb/data \  
-v "lokaler Pfad zum Repository"/couchdb/config:/opt/couchdb/etc/local.d --name couchdb2 couchdb:3</pre>

Aus dem verfassten Dockerfile kann nun eine Art Containerbauplan, das Containerimage, gebaut werden. Dazu muss ein "docker build"-Befehl ausgeführt werden, mit den Parametern des Zielorts und des Ursprungsorts des Dockerfiles.
***Docker build:***  
<pre>docker build -t distributedsystems .</pre>  

Ist das Image nun erstellt, können anhand dessen beliebig viele Container, mit dem Befehl "docker run", hochgefahren werden. Der Port des Containers wird zum lokalen Port gemappt, um auf die enthaltene API zugreifen zu können. Damit der entwickelte Mikroservice mit dem Container kommunizieren kann, welcher die CouchDB zur Verfügung stellt, werden beide Container mit einem alias im gemeinsamen Netzwerk "lib-network" gestartet. Zum Schluss des Befehls wird das Image angegeben, aus welchem der Container entstehen soll.  
***Docker run:***
<pre>docker container run -d -p 8080:8080 --name libraryAPI --network lib-network --network-alias libraryAPI distributedsystems</pre>

## Kubernetes Deployment

minikube start --cpus 2 --memory 3900 --driver docker

CouchDB nach anleitung:
kubectl apply -f couchdb_deployment-main/deploy_couchdb/secret.yaml
kubectl apply -f couchdb_deployment-main/deploy_couchdb/storage.yaml
kubectl apply -f couchdb_deployment-main/deploy_couchdb/service.yaml
kubectl apply -f couchdb_deployment-main/deploy_couchdb/deployment.yaml

minikube service couchdb --> neues Terminal

(MAC) kubectl port-forward service/couchdb 5984:5984 --> neues Terminal

bash couchdb_deployment-main/create_library_db.sh
<pre>
CouchDB Adresse (default: localhost)
localhost
CouchDB Port (default: 5984)
5984
CouchDB User (default: admin)
admin
CouchDB Passwort (default: student)
student
Ziel-URL: admin:student@localhost:5984
========================================

{"ok":true}
{"ok":true,"id":"32ef6b4c46f692868232bd63aa00083b","rev":"1-8a0442e0e9593a70fab0b9c896ce3020"}
{"ok":true,"id":"32ef6b4c46f692868232bd63aa001732","rev":"1-1e03b29451eba02a1230d6df0ee6dd22"}
{"ok":true,"id":"32ef6b4c46f692868232bd63aa002449","rev":"1-6aa5738704d4b157e71a5caa91cbc602"}
{"ok":true,"id":"32ef6b4c46f692868232bd63aa00331b","rev":"1-43359471fd9825330cc0d94c6997ecb3"}
{"ok":true,"id":"32ef6b4c46f692868232bd63aa0038a6","rev":"1-af77b521ee80b1b47e3714129c2bf982"}
{"ok":true,"id":"_design/books","rev":"1-d4df4247f10eea3ebd916124bc44b3d7"}
</pre>

minikube image load distributedsystems:latest

kubectl apply -f deployment/service.yaml

kubectl apply -f deployment/deployment.yaml

minikube service library-api --> neues Terminal

(MAC) kubectl port-forward service/library-api 8080:8080 --> neues Terminal

