"""Module system to import Svelte"""
from __future__ import annotations

from typing import Callable
from collections.abc import MutableMapping

import inspect
import json
from os.path import exists

from .helpers import js_val

_encoder = json.JSONEncoder(ensure_ascii=False)


class Module:
    """Svelte component representable as Python"""

    def __init__(self, path: str, file: str) -> None:
        self._path = path
        self._props: MutableMapping[str, str] = {}
        self._apis: list[Callable] = []
        self._file = file
        self._linker_code: str

    def add_props(self, **props: str) -> Module:
        """Add props to a Svelte component to be referenced"""
        for k, v in props.items():
            self._props[k] = v
        return self

    def set_apis(self, *funcs: Callable) -> Module:
        """Set functions to work as interoping APIs (@<app>.backend is preferred)"""
        self._apis.extend(funcs)
        return self

    def create_linker(self) -> str:
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

        self._linker_code = linker
        return linker

    def create_html(self) -> None:
        """Programmatically create HTML from the imported Svelte code"""
        # NOTE: This API doesn't seem to be used; Consider deprecating soon
        from . import builder

        builder.create_html(self._linker_code)

    def create_api(self) -> str:
        """Programmatically create an API from the functions defined"""
        from . import builder

        api = builder.create_api(self._apis, self._file)
        return api

    def create_interface(self) -> tuple[str, bool]:
        """Create a JavaScript interface for a Spylt API"""
        from . import builder

        interface, suggest = builder.create_interface(self._apis, self._file)
        return "\n\n".join(interface), suggest

    def __call__(self, *args) -> Callable:
        """Create a function which converts to a Quart API route"""
        return self.set_apis(*args)


def require_svelte(path: str) -> Module:
    """Functional importing of Svelte code"""
    if not exists(path):
        raise FileNotFoundError("Svelte file doesn't exist")
    return Module(path, inspect.stack()[1][1])
