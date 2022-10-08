# spylt
A full-stack framework which converts Python functions into usable APIs which can be accessed from easily integrable Svelte code.

```py
# App.py
from spylt import require, apify

app = require("./App.svelte")
app.props(text="Loading...")

app.linker("./main.js")
app.transpile("./app.html")
```

```js
// App.svelte

<script>
    export let text;
    setTimeout(() => text = "Hello world!", 5000)
</script>
<p>{text}</p>
```

Inspired by [PySvelte](https://github.com/anthropics/PySvelte)
