from spylt import require_svelte

app = require_svelte("./src/App.svelte")

app.add_props(text="Pooping...")
app.add_props(age="Pooping...")

app.create_linker("./src/main.js")
