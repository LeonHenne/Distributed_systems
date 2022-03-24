# CouchDB_Deployment

Deploy CouchDB on Docker and K8s

[Offizielles Container Image](https://hub.docker.com/_/couchdb)

## bwLehrpool

In der **bwLehrpool**-Umgebung ist CouchDB bereits lokal installiert und als Single Node grund-konfiguriert.

Userid/Passwort: admin/student

## Als Container in Docker / Podman

Man kann 'docker' durch 'podman' ersetzen.

```
$ docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=student --name couchdb couchdb:3
```

* CouchDB Version 3 ("latest" zum jetzigen Zeitpunkt)
* Expose port 5984
* Admin user/password: admin/student
* ABER: Keine Persistenz!

#### Persisting data and configuration

Ein Directory couchdb/data z.B. im home directory anlegen.
CouchDB Datenbanken und Datenobjekte (shards) werden dann dort angelegt.

Parallel ein Directory couchdb/config anlegen, persistant storage für Config, Benutzer, etc. in Datei docker.ini

```
$ docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=student \
  -v {somedir}/couchdb/data:/opt/couchdb/data \
  -v {somedir}/couchdb/config:/opt/couchdb/etc/local.d --name couchdb couchdb:3
```

Z.B.

```
$ docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=student \
  -v /home/harald/couchdb/data:/opt/couchdb/data \
  -v /home/harald/couchdb/config:/opt/couchdb/etc/local.d --name couchdb couchdb:3

```


#### Web UI Fauxton

[http://localhost:5984/_utils/](http://localhost:5984/_utils/)

### WICHTIG!!!! Basic config

1. In Fauxton anmelden (admin/student)
2. "Setup" tab (Schraubenschlüsselicon), "Configure a Single Node" anklicken, Login credentials eingeben (admin/student)
3. "Configure Node" anklicken. Done
4. "Databases" tab: Es sollte eine _replicator und _users DB geben

---

## Deployment in Kubernetes / Minikube

Config Files im Verzeichnis /deploy_couchdb

#### Environment Variables

K8s secret, creates the 2 env vars for admin user and password.

*secret.yaml:*

```
apiVersion: v1
kind: Secret
metadata:
  name: couchdb-secret
type: Opaque
data:
  COUCHDB_USER: YWRtaW4=  ## admin
  COUCHDB_PASSWORD: c3R1ZGVudA==  ## student
```

```
$ kubectl apply -f secret.yaml
```

#### PV , PVC

* Create 2 persistant storage volumes of type hostpath for config (1 MiB) and data (100 MiB).
* Create a Persistant Volume Claim for each.

*storage.yaml:*

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: config-pv
spec:
  storageClassName: hostpath
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 1Mi
  hostPath:
    path: /data/pv0001/
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: data-pv
spec:
  storageClassName: hostpath
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 100Mi
  hostPath:
    path: /data/pv0002/
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: config-pv-claim
spec:
  storageClassName: hostpath
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pv-claim
spec:
  storageClassName: hostpath
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
---
```

```
$ kubectl apply -f storage.yaml
```

#### Service with NodePort

Provide a NodePort for external access.

*service.yaml:*

```
apiVersion: v1
kind: Service
metadata:
  name: couchdb
  labels:
    app: couchdb
spec:
  type: NodePort
  ports:
    - port: 5984 
      name: http
  selector:
    app: couchdb
```

```
$ kubectl apply -f service.yaml
```

#### Deployment

Ties everything together.

*deployment.yaml:*

```
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: couchdb
  labels:
    app: couchdb
spec:
  selector:
    matchLabels:
      app: couchdb
  template:
    metadata:
      labels:
        app: couchdb
    spec:
      volumes:
      - name: data-storage
        persistentVolumeClaim:
          claimName: data-pv-claim
      - name: config-storage
        persistentVolumeClaim:
          claimName: config-pv-claim
      containers:
      - image: docker.io/library/couchdb:3
        name: couchdb
        ports:
        - containerPort: 5984
        volumeMounts:
        - mountPath: "/opt/couchdb/data"
          name: data-storage
        - mountPath: "/opt/couchdb/etc/local.d"
          name: config-storage
        env:
        - name: COUCHDB_USER
          valueFrom:
            secretKeyRef:
              name: couchdb-secret
              key: COUCHDB_USER
        - name: COUCHDB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: couchdb-secret
              key: COUCHDB_PASSWORD
```

```
$ kubectl apply -f deployment.yaml
```

Aufruf im Browser:

```
$ minikube service couchdb
```


## Using CouchDB REST API

[https://docs.couchdb.org/en/stable/intro/tour.html](https://docs.couchdb.org/en/stable/intro/tour.html)

```bash
$ curl http://127.0.0.1:5984/ | jq .

{
  "couchdb": "Welcome",
  "version": "3.1.2",
  "git_sha": "572b68e72",
  "uuid": "b568c0950cd170b6af1181e88f278e14",
  "features": [
    "access-ready",
    "partitioned",
    "pluggable-storage-engines",
    "reshard",
    "scheduler"
  ],
  "vendor": {
    "name": "The Apache Software Foundation"
  }
}
```

List all databases

```bash
$ curl -X GET http://admin:student@127.0.0.1:5984/_all_dbs
["_replicator","_users"]
```

Create a database

```bash
$ curl -X PUT http://admin:student@127.0.0.1:5984/albums
{"ok":true}
```

Delete a database

```bash
$ curl -X DELETE http://admin:student@127.0.0.1:5984/albums
{"ok":true}
```

usw.

## Tutorial

https://dev.to/yenyih/query-in-apache-couchdb-views-4hlh


## Basis für Prüfungsaufgabe

### Grundkonfiguration muss nach der CouchDB-Installation einmal ausgeführt werden

1. In Fauxton anmelden (admin/student)
    [http://localhost:5984/_utils/](http://localhost:5984/_utils/)
2. "Setup" tab (Schraubenschlüsselicon), "Configure a Single Node" anklicken, Login credentials eingeben (admin/student)
3. "Configure Node" anklicken. Done
4. "Databases" tab: Es sollte eine _replicator und _users DB geben


### Datenbank, Daten, Views und Anwendungsbeispiele

* Externe URL für CouchDB lokal in der bwLehrpool-Umgebung oder in Docker:  http://admin:student@localhost:5984
* In Minikube über ‚minikube service list‘ für den eigenen Rechner abfragen.

**Datenstrukturen und Daten** entweder anlegen mit dem Skript `create_library_db.sh` (fragt die Verbindungsdaten ab) oder manuell mit diesen Schritten:

1. **Datenbank** anlegen ("library"):

	```
	curl -X PUT http://admin:student@127.0.0.1:5984/library
	```

2. Einige **Records** (= Bücher) hinzufügen:

	CouchDB erzeugt automatisch die UUID für _id. Daten von 5 Büchern jeweils in JSON Objekt: author, title, lang(uage), isbn.

	```
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d '{"author": "King, Stephen", "title": "Es", "lang": "de", "isbn": "978-3-453-43577-3"}' 
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d '{"author": "King, Stephen", "title": "Friedhof der Kuscheltiere", "lang": "de", "isbn": "978-3-453-44160-6"}'
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d '{"author": "Irving, John", "title": "The Hotel New Hampshire", "lang": "en", "isbn": "978-0-345-40047-5"}'
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d '{"author": "Melandri, Francesca", "title": "Über Meereshöhe", "lang": "de", "isbn": "978-3-8031-2812-6"}'
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d '{"author": "Highsmith,Patricia", "title": "The Talented Mr. Ripley", "lang": "en", "isbn": "978-3-15-009145-6"}'
	```

3. **Views** anlegen: byAuthor, byTitle, byLanguage, byISBN

	```
	curl -H 'Content-Type: application/json' -X POST http://admin:student@127.0.0.1:5984/library -d \
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
	```

### Beispiele für Anwendung:

1. Alle Bücher anzeigen, sortiert nach Author

	```
	curl -X GET http://admin:student@127.0.0.1:5984/library/_design/books/_view/byAuthor | jq .
	```

	Basiert auf View 'byAuthor' 

2.  Query: Nur englische Bücher:

	```
	curl -H 'Content-Type: application/json' -X GET 'http://admin:student@127.0.0.1:5984/library/_design/books/_view/byLanguage?key="en"'
	```

	Basiert auf View 'byLanguage', 'key' ist eigentlich falsch, der Key ist 'document.lang', der Value ist dann 'en'.

	**Achtung:** Der gesamte http:... String muss in einfache Quotes (' '), sonst Fehler ("invalid UTF-8 JSON")

3. Buch in Datenbank eintragen:

	* Ist Buch in Datenbank schon vorhanden?
	* Keine unique keys: **Das selbe Buch** kann **beliebig oft** in CouchDB-Datenbank eingetragen werden!!!
	
	Eine Lösung: Vor Eintrag abprüfen, ob ISBN bereits bekannt ist (ISBN ist per se ein unique key).
	
	Query bei nicht vorhandener ISBN:

	```
	curl -H 'Content-Type: application/json' -X GET 'http://admin:student@127.0.0.1:5984/library/_design/books/_view/byISBN?key="978-3-15-009145-5"' |  jq .rows
	[]
	```

	Also kein Fehler, sondern leeres result set rows[]


