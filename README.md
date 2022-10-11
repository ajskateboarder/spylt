# spylt

**This project is very experimental, expect bugs and [caveats](#caveats)**

**Spylt (*spilt*)** is a full-stack web framework which simplifies backend development and frontend development. Simple Python functions can be turned into web APIs which can be directly called from Svelte code **under a single codebase.**  

No directory structure is forced, making Spylt very unopinionated and scalable when organizing code.

## Why?

Normally, if you wanted to combine an API and a frontend framework, you would have to separate the apps into different codebases and different repositories. 

The ideal solution would be to simply store frontend code in a single application, similar to how classic SSR sites work. Instead of storing HTML pages however, it would have Svelte pages, which allow for better modularity and more reactivity. (This isn't possible to actually do, but such behavior can be emulated.)

**This is your solution.**

In addition, the whole site can be created and built automatically into a [Quart](https://quart.palletsprojects.com/) app with compiled Svelte code and even backend API routes!  

## Simple usage

Create a new project:

```bash
python3 -m spylt new <dir>
```

This installs required NPM packages and creates a `rollup.config.js` for compiling Svelte to JS/CSS/HTML. This is the default config for `sveltejs/template`. You can configure Rollup to support TypeScript and SCSS. 

There should also be an `src/` directory with an `App.py` and an `App.svelte`. The svelte code should have a `point` comment and a `compiled` comment. This is special syntax used by Spylt for a more seamless DX.

### `<!-- point *.py -->`
This syntax is used for more seamless compilation when compiling Svelte code. Spylt checks this comment when compiling a Svelte file to pass any props into the built HTML.

### `<!-- compiled *.html -->`
This comment is also checked by Spylt when "rendering" Svelte code.

Compile the Svelte to HTML with:

```bash
python3 -m spylt html ./src/App.svelte ./index.html
```

Building Svelte routes with APIs are as simple as this:

```py
import requests
from spylt import require_svelte

app = require_svelte("./App.svelte")

@app.backend
def search(query: str):
    r = requests.get(f"https://dummyjson.com/products/search?q={query}")
    return r.json()

@app.frontend("/")
def root():
    return app.render("")

print(app.create_api("./dump.py"))
```

## Caveats
- `src.*` imports are ignored in APIs. Consider dumping the API with `app.create_api("path/to/file.py")` and fixing errors manually.
- 

#

Inspired by [PySvelte](https://github.com/anthropics/PySvelte)
