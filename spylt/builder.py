"""
Automation tools to compile Svelte to direct HTML
and compile Spylt functions to APIs

Prefer to use Module instances or :func:`require_svelte <spylt.module.require_svelte>`
"""
from __future__ import annotations

# This is to inspect for types in _create_api()
import builtins
import typing

from typing import Callable

import os
import re
import runpy
from itertools import chain
from shutil import rmtree
from shlex import quote

from inspect import getsourcelines

try:
    from inspect import get_annotations
except ImportError:  # 3.8 compatibility
    from get_annotations import get_annotations

import black
import isort

from .exceptions import NoRoutesDefinedError, TypesNotDefinedError
from .helpers import flatten_dict, replace_some
from .module import Module

_N, _Q = "\n", '"'
_F, _B = (
    "{",
    "}",
)

_HTML_F = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>{}</style>
</head>
<body>
    <script>
        function fetchSync(url) {{
            const xhr = new XMLHttpRequest();
            xhr.open('GET', url, false);
            xhr.send();

            if (xhr.status === 200) {{
                return JSON.parse(xhr.responseText);
            }} else {{
                throw new Error('Failed to fetch data');
            }}
        }}
    </script>
    <script>{}</script>
</body>
</html>"""


def create_link(inp: str) -> str:
    """Creates an app initializer (JavaScript) using a reference to a Python namespace"""
    path, instance = inp.split(":")

    lib = runpy.run_path(path)
    inst = [k for k, v in lib.items() if isinstance(v, Module) and k == instance]

    if inst == []:
        raise RuntimeError(f"Instance of module '{instance}' does not exist.")
    module: Module = lib[inst[0]]

    return module.create_linker()


def create_html(linker: str) -> str:
    """Create HTML from """
    os.system(
        " ".join(
            [
                "echo",
                quote(linker),
                "|",
                "npx rollup --silent --config --file ./__buildcache__/bundle.js",
                ">/dev/null 2>/dev/null"
            ]
        ),
    )
    js = None
    css = None
    if os.path.exists("./__buildcache__/bundle.js"):
        with open("./__buildcache__/bundle.js", "r", encoding="utf-8") as fh:
            js = fh.read().replace('"use strict";', "")
    if os.path.exists("./__buildcache__/bundle.css"):
        with open("./__buildcache__/bundle.css", "r", encoding="utf-8") as fh:
            css = fh.read()
    rmtree("./__buildcache__", ignore_errors=True)
    return (
        re.sub(r"<!--(.*?)-->|\s\B", "", _HTML_F.format("" if not css else css, js))
        .replace("//# sourceMappingURL=bundle.js.map", "")
        .replace("const$", "$")
        .replace("function$", "function $")
    )


def _create_api(functions: list[Callable], source_file: str):
    source_map = {"names": [], "args": [], "types": [], "docs": []}
    sources = []

    with open(source_file, encoding="utf-8") as fh:
        third_party = [
            i
            for i in isort.code(
                black.format_str(fh.read(), mode=black.Mode())
            ).splitlines()
            if i.find("import") != -1 and i.find("spylt") == -1 and i.find("src") == -1
        ]

    for api in functions:
        source = getsourcelines(api)
        source_map["docs"].append(api.__doc__)

        source_map["types"].append(get_annotations(api))
        defined = False
        lines = []
        for line in source[0]:
            if defined:
                if "return" in line:
                    return_obj = line.strip().split(" ", 1)[-1]
                    ret = f"{' ' * (len(line.split(' ')[:-2]) - 1)}return {_F+_Q}response{_Q}: {return_obj}{_B}"
                    spaces = len(ret.split("return")[0])

                    if 4 % spaces != 0:
                        ret = (" " * (4 * round(spaces / 4))) + ret.strip()

                    lines.append(ret)
                else:
                    lines.append(line)
            if line.startswith("def"):
                defpoint = [
                    e.replace(",", "")
                    for e in line.strip()
                    .replace("(", " ")
                    .replace(")", " ")
                    .replace(":", "")
                    .split(" ")[1:-1]
                    if e not in [*dir(typing), *dir(builtins)] and e not in ("", "->")
                ]
                source_map["names"].append(defpoint[0])
                source_map["args"].append(defpoint[1:])
                defined = True
        sources.append(lines)

    source_args = [
        [
            k
            for k in e
            if k not in [*dir(typing), *dir(builtins)] and k not in ("", "->")
        ]
        for e in source_map["args"]
    ]
    type_arg = flatten_dict(
        dict(list(zip(list(chain.from_iterable(source_args)), source_map["types"])))
    )
    if source_args == []:
        raise NoRoutesDefinedError(
            "No routes were defined on the Python backend.\n"
            "You should define backend logic with functions using @app.backend()"
        )

    if not all(x in type_arg for x in source_args[0]):
        raise TypesNotDefinedError(
            f"No types are set on arguments \"{', '.join(source_args[0])}\" "
            "on function {source_map['names'][0]}()\n"
            "Please annotate the arguments so types can be casted correctly"
        )

    return (
        source_map["args"],
        dict(zip(source_map["names"], sources)),
        [[e[1] for e in list(s.items())] for s in source_map["types"]],
        third_party,
        source_map["docs"]
    )


def create_interface(apis: list[Callable], source_file: str) -> list[str]:
    """Create a typed JavaScript interface for a Spylt API"""
    args, source, types, _, docs = _create_api(apis, source_file)
    typemap = {
        "str": "string",
        "list": "any[]",
        "int": "number",
        "bool": "boolean"
    }

    javascripts = []
    for route, args, types, doc in zip(source.keys(), args, types, docs):
        types_ = [typemap.get(typ.__name__, "any") for typ in types[:-1]]
        return_type = typemap.get(types[-1].__name__, "any")

        javascripts.append(
            f"""/**
 * {doc}
{_N.join([f" * @param {{{typ_}}} {arg}" for typ_, arg in zip(types_, args)])}
 * @returns {{{return_type}}}
 */
export function {route}({', '.join(args)}) {{
    const res = fetchSync(`/api/{route}?{'&'.join(list(map(lambda x: x + "=${" + x + "}", args)))}`)
    return res.response
}}"""
        )

    return javascripts


def create_api(apis: list[Callable], source_file: str) -> str:
    """Messy API to check imports and function name + args and convert to a Quart app"""
    args, source, types, imports, _ = _create_api(apis, source_file)

    argmap = [
        {k: f"request.args.get('{k}', type={w.__name__})" for k, w in zip(l, t)}
        for l, t in zip(args, types)
    ]
    argmap = {k: v for d in argmap for k, v in d.items()}

    api_string = (
        f"""{_N.join(imports)}
from quart import Quart, request
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")

@app.route("/")
async def root_():
    with open("index.html", encoding="utf-8") as fh:
        return fh.read()

{_N.join([replace_some(f"@app.route({_Q}/api/{name}{_Q}){_N}async def {name}():{_N}{''.join(lines)}", argmap) for name, lines in source.items()])}
    """[
            :-4
        ].replace(
            "from .module import Module\n", ""
        ).replace(
            "from .helpers import template\n", ""
        )
        + "\napp.run()\n"
    )

    return api_string
