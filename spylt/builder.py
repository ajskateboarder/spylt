"""Automation tools to compile Svelte to direct HTML"""
from os.path import exists
import runpy
import os
from .module import Module

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
    path, instance = inp.split(':')

    lib = runpy.run_path(path)
    inst = [k for k, v in lib.items() if isinstance(v, Module) and k == instance]

    if inst == []:
        raise RuntimeError(f"Instance of module '{instance}' does not exist.")
    lib[inst[0]].create_linker(out)


def build(out):
    os.system(f"npx rollup -c -o {out}")
