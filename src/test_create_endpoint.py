import requests
import json

url = "http://127.0.0.1:3000/api/v1/create"
data = {"author": "Henne, Leon", "title":
"Das Leid der verteilten Systeme", "lang": "de", "isbn": "978-0-345-40047-5"}

result = requests.put(url,json.dumps(data))
print(result)