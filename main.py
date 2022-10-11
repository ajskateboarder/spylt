import requests

from spylt import interopable
from src.App import app


@interopable(app)
def search(query: str):
    req = get(f"https://dummyjson.com/products/search?q={query}")
    return req.json()


app.create_api("api.py")
