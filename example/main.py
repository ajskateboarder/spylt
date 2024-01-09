from pandas import DataFrame
from quart import Quart, request
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")

@app.route("/")
async def root_():
    with open("index.html", encoding="utf-8") as fh:
        return fh.read()

@app.route("/api/say_hello")
async def say_hello():
    name = request.args.get('name', type=str)
    """Says hello to the user"""
    return {"response": f"Hello {name}".to_dict(orient="records")}
@app.route("/api/scream_hello")
async def scream_hello():
    name = request.args.get('name', type=str)
    """Screams hello to the user"""
    return {"response": f"HELLO {name.upper()}!!"}

app.run()
