# spylt

**This project is very experimental, expect bugs and [caveats](#caveats)**

**Spylt** (*pronounced spilt, combination of Svelte and Python*) is a connector for Python HTTP backends and Svelte frontends. Simple Python functions can be turned into web APIs which can be directly called from Svelte code **under a single codebase.**

Spylt can currently be used for SPAs, but multi-page support can definitely be added.

## Why?

Normally, if you wanted to combine an API and a frontend framework, you would have to separate the apps into different codebases and different repositories. 

The ideal solution would be to simply store frontend code in a single application, similar to how classic SSR sites work. Instead of storing HTML pages however, it would have Svelte pages, which allow for better modularity and more reactivity.

This is what Spylt aims to do. Spylt works best for demo apps (like [Streamlit](https://streamlit.io) or [Gradio](https://gradio.app)) that need more control over JavaScript/CSS. Since Spylt also uses Svelte for the frontend, it can outperform libraries like [Pynecone](https://pynecone.io/) and [Plotly Dash](https://dash.plotly.com/).

## Simple usage

Install spylt with `pip`:

```bash
git clone https://github.com/lemystic/spylt
cd spylt
pip install -r requirements.txt
pip install -e .
```

Initialize a starter project with `spylt new`:

```bash
python3 -m spylt new <dir>
cd <dir>
```




## Caveats
Most of the caveats can be fixed manually by dumping the API with `app.create_api("path/to/file.py")` and fixing errors manually.

- Using multiple parameters for functions creates completely wrong code

- `src.*` imports are ignored when compiling backend routes

- Backend routes are strictly named after functions and cannot be defined without editing

- Backend route parameters, when compiled, expect values to be passed through query params. This is obviously not secure for certain cases. (Support for POSTing can be added in the future)

- Mentioned parameters require type annotations

- Using single-quotes for F-strings can cause syntax errors in the compiled API (just follow PEP8)

#

Inspired by [PySvelte](https://github.com/anthropics/PySvelte)
