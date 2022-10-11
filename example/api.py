import requests
from src.App import app

@app.interopable
def search(query: str):
    r = requests.get(
        f"https://dummyjson.com/products/search?q={query}"
    )
    return r.json()

print(app.create_api("./dump.py"))