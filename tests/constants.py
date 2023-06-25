PY_MODULE = """from spylt import require_svelte

app = require_svelte("{tempdir}/App.svelte")


@app.backend()
def say_hello(name: str) -> str:
    '''Says hello to the user'''
    return f"Hello {{name}}"
""".format

SVELTE_MODULE = """<!-- point ./App.py:app -->
<script>
    const say_hello = async (name) => { 
        request = await fetch(`/api/say_hello?name=${name}`)
        json = await request.json()
        return json.response
    }

    let greeting
    let name = "Bob"
</script>
<main>
    <input type="text" bind:value={name}>
    <button on:click={(async function() { greeting = await say_hello(name) })()}>Say hello</button>
    <p>{greeting}</p>
</main>"""
