"""Module system to import Svelte"""
import inspect
import json
import os
import runpy
from os.path import exists

from .helpers import js_val

_encoder = json.JSONEncoder(ensure_ascii=False)


class Module:
    """Svelte component representable as Python"""

    def __init__(self, path: str, file: str) -> None:
        self._path = path
        self._props = {}
        self._apis = []
        self._file = file
        self._linker = None

    def add_props(self, **props):
        """Add props to a Svelte component to be referenced"""
        for k, v in props.items():
            self._props[k] = v
        return self

    def set_apis(self, *funcs):
        """Set functions to work as interoping APIs (@<app>.backend is preferred)"""
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

    def create_api(self, dump=None, get_string=False):
        """Programmatically create a Sanic API from the functions defined"""
        # TODO: Make this code less bad
        from . import builder

        self._file = inspect.stack()[1][1]

        api = builder.create_api(self._apis, self._file)
        if get_string:
            return api

        with open(dump or "/tmp/spylt_api.py", "w", encoding="utf-8") as fh:
            fh.write(api)

        if not dump:
            try:
                return runpy.run_path("/tmp/spylt_api.py")["app"].run
            finally:
                os.remove("/tmp/spylt_api.py")

    def backend(self):
        """Create a function which converts to a Quart API route"""

        def wrapper(*args):
            ret = self.set_apis(*args)
            return ret

        return wrapper


def require_svelte(path: str):
    """Functional importing of Svelte code"""
    if not exists(path):
        raise FileNotFoundError("Svelte file doesn't exist")
    return Module(path, inspect.stack()[1][1])
