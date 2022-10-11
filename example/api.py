import requests
from src.App import app


@app.backend()
def search(query: str):
    r = requests.get(f"https://dummyjson.com/products/search?q={query}")
    return r.json()


app.create_api("./dump.py")
