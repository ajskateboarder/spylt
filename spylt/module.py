"""Module system to import Svelte"""
import json
from typing import Callable
from os.path import exists
import inspect
import runpy

from .helpers import js_val


_encoder = json.JSONEncoder(ensure_ascii=False)


class Module:
    """Svelte component representable as Python"""

    def __init__(self, path: str, file: str) -> None:
        self._path = path
        self._props = {}
        self._apis = []
        self.file = file
        self._linker = None

    def add_props(self, **props):
        """Add props to a Svelte component to be referenced"""
        for k, v in props.items():
            self._props[k] = v
        return self

    def set_apis(self, *funcs: Callable):
        """Set functions to work as interoping APIs (@interop is preferred)"""
        self._apis.extend(funcs)
        return self

    def create_linker(self, path: str):
        """Programmatically create a linking main.js file with any props"""
        _newline = "\n"
        linker = f"""import App from '{self._path}';

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

        self._linker = path
        return self

    def create_html(self, path: str):
        """Programmatically create HTML from the imported Svelte code"""
        from . import builder

        builder.create_html(path, self._linker)

    def create_api(self, dump=None):
        """Programmatically create a Sanic API from the functions defined"""
        from . import builder
        self.file = inspect.stack()[1][1]

        api = builder.create_api(self._apis, self.file)
        with open(dump or "/tmp/spylt_api.py", "w", encoding="utf-8") as fh:
            fh.write(api)
        return runpy.run_path("/tmp/spylt_api.py")["app"] if not dump else None

    @property
    def interopable(self):
        """Create a function which converts to a Sanic API route"""

        def wrapper(*args):
            ret = self.set_apis(*args)
            return ret

        return wrapper


def require_svelte(path: str):
    """Functional importing of Svelte code"""
    if not exists(path):
        raise RuntimeError("Svelte file doesn't exist")
    return Module(path, inspect.stack()[1][1])
