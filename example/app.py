from quart import Quart, request

app = Quart(__name__)

@app.route("/api/addition")
async def addition():
    return {"response": request.args.get("one", type=int) + request.args.get("two", type=int)}

@app.route("/api/hello")
async def hello():
    return {"response": "Hello {}!".format(request.args.get("name", type=str))}
