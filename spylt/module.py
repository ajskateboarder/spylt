"""Module system to import Svelte"""
import json
from typing import Callable
from os.path import exists
from .helpers import js_val

_encoder = json.JSONEncoder(ensure_ascii=False)


class Module:
    def __init__(self, path: str) -> None:
        self._path = path
        self._props = {}
        self._api = None

    def add_props(self, **props):
        """Add props to a Svelte component to be referenced"""
        for k, v in props.items():
            self._props[k] = v
        return self

    def set_api(self, func: Callable):
        """Set a function to work as an interoping API (decorator is preferred)"""
        self._api = func

    def create_linker(self, path: str):
        _newline = "\n"
        linker = f"""import App from '{self._path.replace('./src/', './')}';

        const app = new App({{
            target: document.body,
            props: {{
              {js_val(_encoder, self._props).replace("{", "").replace("}", "").replace(", ", f",{_newline}      ")}
            }}
        }});

        export default app;""".replace(
            "        ", ""
        )

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(linker)
        return self

    def build(self, path: str):
        from .builder import build as _build

        _build(path)


def require_svelte(path: str):
    """Functional importing of Svelte code"""
    if not exists(path):
        raise RuntimeError("Svelte file doesn't exist")
    return Module(path)
