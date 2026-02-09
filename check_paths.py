import requests
import json

try:
    r = requests.get("http://127.0.0.1:8000/openapi.json")
    if r.status_code == 200:
        data = r.json()
        print("Registered Paths:")
        for path in data.get("paths", {}).keys():
            print(path)
    else:
        print(f"Failed to get openapi.json: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
