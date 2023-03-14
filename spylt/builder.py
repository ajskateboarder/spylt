"""Automation tools to compile Svelte to direct HTML"""
import os
import os.path
import re
import runpy
from functools import reduce
from inspect import getsourcelines
from itertools import chain
from shutil import rmtree

try:
    from inspect import get_annotations
except ImportError: # 3.8 compatibility
    from get_annotations import get_annotations

import black
import isort

from .exceptions import NoRoutesDefinedError, TypesNotDefinedError
from .helpers import flatten_dict, replace_some
from .module import Module

_N, _Q = "\n", '"'

_REQ = [
    "@rollup/plugin-commonjs",
    "@rollup/plugin-node-resolve",
    "rollup",
    "rollup-plugin-css-only",
    "rollup-plugin-livereload",
    "rollup-plugin-svelte",
    "rollup-plugin-terser",
    "svelte",
]

_HTML_F = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>{}</style>
</head>
<body>
    <script defer>{}</script>
</body>
</html>"""


def pr_exists(name):
    return os.system(f"which {name}") == 0


def copy_rollup():
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "rollup.config.txt"),
        encoding="utf-8",
    ) as fh:
        with open("./rollup.config.js", "w", encoding="utf-8") as fh_:
            fh_.write(fh.read())


def template(directory):
    if os.path.exists(directory):
        raise FileExistsError(
            "Directory already exists. Choose a directory that doesn't exist yet."
        )

    os.mkdir(directory)
    os.chdir(directory)

    if not pr_exists("npm"):
        raise RuntimeError(
            "Node and NPM are not installed.\n"
            "Consider installing with NVM:\n"
            "https://github.com/nvm-sh/nvm#installing-and-updating"
        )
    os.system("npm init --y >/dev/null")
    os.system(f"npm install --save-dev {' '.join(_REQ)} >/dev/null")
    os.system("npm install sirv-cli >/dev/null")

    if os.path.exists("./rollup.config.js"):
        inp = input(
            "You seem to have a Rollup config here already. "
            "Do you want to update it or leave it alone? (Y/n)"
        )
        if inp in ("N", "n"):
            return
    copy_rollup()
    os.mkdir("src")
    with open("src/App.svelte", "w", encoding="utf-8") as fh:
        fh.write(
            """<!-- point ./src/App.py:app -->
<script>
    export let text
    setTimeout(() => text = "Hello world!", 5000)
</script>
<main>
    <p>{text}</p>
</main>
        """
        )
    with open("src/App.py", "w", encoding="utf-8") as fh:
        fh.write(
            """from spylt import require_svelte

app = require_svelte("./src/App.svelte")
app.add_props(text="Loading...")
        """
        )

    print(
        "* Project initialized successfully! *\n"
        "Now you can setup a simple project and run: "
        "`python3 -m spylt build`"
    )


def create_link(inp, out):
    path, instance = inp.split(":")

    lib = runpy.run_path(path)
    inst = [k for k, v in lib.items() if isinstance(v, Module) and k == instance]

    if inst == []:
        raise RuntimeError(f"Instance of module '{instance}' does not exist.")
    lib[inst[0]].create_linker(out)


def create_html(out, linker):
    os.system(f"npx rollup --config --input={linker} -o ./__buildcache__/bundle.js")
    js = None
    css = None
    if os.path.exists("./__buildcache__/bundle.js"):
        with open("./__buildcache__/bundle.js", "r", encoding="utf-8") as fh:
            js = fh.read().replace('"use strict";', "")
    if os.path.exists("./__buildcache__/bundle.css"):
        with open("./__buildcache__/bundle.css", "r", encoding="utf-8") as fh:
            css = fh.read()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(
            re.sub(
                r"<!--(.*?)-->|\s\B", "", _HTML_F.format("" if not css else css, js)
            ).replace("//# sourceMappingURL=bundle.js.map", "").replace("const$", "$")
        )

    try:
        rmtree("./__buildcache__")
    except FileNotFoundError:
        pass


def _create_api(functions, source_file):
    source_map = {"names": [], "args": [], "types": []}
    sources = []
    (
        _F,
        _B,
    ) = (
        "{",
        "}",
    )

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

        source_map["types"].append(get_annotations(api))
        defined = False
        lines = []
        for line in source[0]:
            if defined:
                if "return" in line:
                    return_obj = line.strip().split(" ", 1)[-1]
                    ret = f"{' ' * (len(line.split(' ')[:-2]) - 1)}return {_F+_Q}response{_Q}: {return_obj}{_B}"
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
                ]
                source_map["names"].append(defpoint[0])
                source_map["args"].append(defpoint[1:])
                defined = True
        sources.append(lines)

    source_args = [
        [k for k in e if not k in ("int", "str") and k != ""]
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
    )


def create_api(apis, source_file):
    """Messy API to check imports and function name + args and convert to a Quart app"""
    args, source, types, imports = _create_api(apis, source_file)
    argmap = [
        {k: f"request.args.get('{k}', type={w.__name__})" for k, w in zip(l, t)}
        for l, t in zip(args, types)
    ]
    argmap = {k: v for d in argmap for k, v in d.items()}

    QUERY = f"""{_N.join(imports)}
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
        :-5
    ]

    return QUERY
