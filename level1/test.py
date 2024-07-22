import json

import requests

url = "http://127.0.0.1:8000/chat"
message = "write fibinacci series program in python"
data = {"content": message}

headers = {"Content-type": "application/json"}

with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)