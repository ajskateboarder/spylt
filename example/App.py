from spylt import interopable, require_svelte

app = require_svelte("./App.svelte")

app.add_props(text="Loading...")