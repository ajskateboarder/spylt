from spylt import require_svelte, interop

app = require_svelte("./App.svelte")

app.add_props(text="Pooping...")
app.add_props(age="Pooping...")


@interop(app)
def say_hi():
    return "Hello world!"
