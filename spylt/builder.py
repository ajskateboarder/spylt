"""Automation tools to compile Svelte to direct HTML"""
from itertools import chain
from os.path import exists
from shutil import rmtree
from inspect import get_annotations, getsourcelines
from functools import reduce
import os
import re
import runpy

from .module import Module
from .helpers import replace_some


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

_ROLLUP_CFG = (
    "https://raw.githubusercontent.com/sveltejs/template/master/rollup.config.js"
)

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
    if os.system(f"which {name}") == 0:
        return True
    return False


def curl_rollup():
    if pr_exists("curl"):
        os.system(f"curl {_ROLLUP_CFG} -o ./rollup.config.js")
    elif pr_exists("wget"):
        os.system(f"wget {_ROLLUP_CFG}")
    else:
        raise RuntimeError(
            "cURL / Wget are not installed. "
            "Install either program with your system's package manager."
        )


def initialize():
    if not pr_exists("npm"):
        raise RuntimeError(
            "Node and NPM are not installed.\n"
            "Consider installing with NVM:\n"
            "https://github.com/nvm-sh/nvm#installing-and-updating"
        )
    os.system("npm init --y")
    os.system(f"npm install --save-dev {' '.join(_REQ)}")
    os.system("npm install sirv-cli")

    if exists("./rollup.config.js"):
        inp = input(
            "You seem to have a Rollup config here already. "
            "Do you want to update it or leave it alone? (Y/n)"
        )
        if inp in ("N", "n"):
            return
    curl_rollup()
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
    os.system(f"npx rollup -c --silent --input={linker} -o ./__buildcache__/bundle.js")
    js = None
    css = None
    if exists("./__buildcache__/bundle.js"):
        with open("./__buildcache__/bundle.js", "r", encoding="utf-8") as fh:
            js = fh.read()
    if exists("./__buildcache__/bundle.css"):
        with open("./__buildcache__/bundle.css", "r", encoding="utf-8") as fh:
            css = fh.read()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(
            re.sub(
                r"<!--(.*?)-->|\s\B", "", _HTML_F.format("" if not css else css, js)
            ).replace("//# sourceMappingURL=bundle.js.map", "")
        )

    rmtree("./__buildcache__")


def _create_api(functions):
    source_names = []
    source_args = []
    source_types = []
    sources = []
    _F, _B, _Q = "{", "}", '"'

    for api in functions:
        source = getsourcelines(api)
        source_types.append(get_annotations(api))
        defined = False
        lines = []
        for line in source[0]:
            if defined:
                if "return" in line:
                    ret = f"{line.strip().replace(' ', f' {_F}{_Q}response{_Q}: ', 1)}{_B}"
                    lines.append(ret)
                else:
                    lines.append(line.strip())
            if line.startswith("def"):
                defpoint = [
                    e.replace(",", "")
                    for e in line.strip()
                    .replace("(", " ")
                    .replace(")", " ")
                    .replace(":", "")
                    .split(" ")[1:-1]
                ]
                source_names.append(defpoint[0])
                source_args.append(defpoint[1:])
                defined = True
        sources.append(lines)

    source_args = [
        [k for k in e if not k in ("int", "str") and k != ""] for e in source_args
    ]
    source_types = [[e[1] for e in list(s.items())] for s in source_types]
    type_arg = dict(zip(list(chain.from_iterable(source_args)), source_types))

    if not all(x in type_arg for x in source_args[0]):
        raise RuntimeError(
            f"No types are set on arguments \"{', '.join(source_args[0])}\" on function {source_names[0]}()\n"
            "Please annotate the arguments so types can be casted correctly"
        )
    
    return source_args, dict(zip(source_names, sources)), source_types


def create_api(apis):
    _N, _Q, _NN = "\n    ", '"', "\n"
    args, source, types = _create_api(apis)
    print(types)
    argmap = reduce(
        lambda x, y: x | y, [{k: f"request.args.get(\"{k}\", type={w.__name__})" for k, w in zip(l, t)} for l, t in zip(args, types)], {}
    )

    return f"""from quart import Quart, request

        app = Quart(__name__)

        {_NN.join([replace_some(f"@app.route({_Q}/api/{name}{_Q}){_NN}async def {name}():{_N}        {_NN.join(lines)}{_NN}", argmap) for name, lines in source.items()])}
    """.replace("        ", "")[:-5]
