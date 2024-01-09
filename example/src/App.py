from spylt import require_svelte
from pandas import DataFrame

app = require_svelte("./src/App.svelte")

@app
def say_hello(name: str) -> DataFrame:
    """Says hello to the user"""
    return f"Hello {name}"

@app
def scream_hello(name: str) -> str:
    """Screams hello to the user"""
    return f"HELLO {name.upper()}!!"
