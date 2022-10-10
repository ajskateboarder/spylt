from spylt import require_svelte, interopable

app = require_svelte("./App.svelte")

app.add_props(name="loading...")


@interopable(app)
def addition(one: int, two: int):
    return one + two


@interopable(app)
def hello(name: str):
    return "Hello {}!".format(name)


app.create_api("./app.py")
