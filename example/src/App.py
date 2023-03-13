from spylt import require_svelte

app = require_svelte("./src/App.svelte")

@app.backend()
def say_hello(name: str):
    return f"Hello {name}"