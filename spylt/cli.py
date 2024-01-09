"""The CLI, I guess"""
from argparse import ArgumentParser, Namespace
import shutil
import os
import time
import sys

from pathlib import Path
from runpy import run_path

from rich.console import Console
from rich.markdown import Markdown

from . import builder
from .helpers import find_pointer
from .module import Module


console = Console(log_path=False, log_time=False)
REQUIREMENTS = [
    "@rollup/plugin-commonjs",
    "@rollup/plugin-node-resolve",
    "rollup",
    "rollup-plugin-css-only",
    "rollup-plugin-livereload",
    "rollup-plugin-svelte",
    "rollup-plugin-terser",
    "svelte",
]


def new(namespace: Namespace) -> None:
    """Scaffold a new Spylt project"""
    if Path(namespace.directory).exists():
        console.log(f"𐄂 {namespace.directory} already exists as a directory")
        sys.exit(1)

    start = time.time()

    os.makedirs(Path(namespace.directory) / "src")
    os.chdir(namespace.directory)

    if not os.system("which npm >/dev/null") == 0:
        console.log(
            "𐄂 Node and NPM are not installed. Consider installing with NVM:\n"
            "https://github.com/nvm-sh/nvm#installing-and-updating"
        )
        sys.exit(1)

    with console.status("Installing required dependencies..."):
        os.system("npm init --y >/dev/null")
        os.system(
            f"npm install --save-dev {' '.join(REQUIREMENTS)} >/dev/null 2>/dev/null"
        )
        os.system(
            f"pip install json2html >/dev/null 2>/dev/null"
        )

    shutil.copyfile(
        Path(__file__).parent / "rollup.config.js.txt",
        "./rollup.config.js",
    )

    with open("src/App.svelte", "w", encoding="utf-8") as fh:
        fh.write(
            """<!-- point ./src/App.py:app -->
<script>
    let text
    import { say_hello } from "./api"
</script>
<main>
    <p>Welcome to Spylt</p><br>
    <input type="text" name="Name" bind:value={text}>
    <button type="submit" on:click={() => alert(say_hello(text))}>Greet</button>
</main>
        """
        )
    with open("src/App.py", "w", encoding="utf-8") as fh:
        fh.write(
            '''from spylt import require_svelte

app = require_svelte("./src/App.svelte")

@app.backend()
def say_hello(name: str) -> str:
    """Says hello to the user"""
    return f"Hello {name}"

@app.backend()
def scream_hello(name: str) -> str:
    """Screams hello to the user"""
    return f"HELLO {name.upper()}!!"
        '''
        )
    end = time.time()

    console.log(
        Markdown(
            f"""✓ Project {namespace.directory} scaffolded in {end - start:.2f}s.
You can now run the following to get started:
```bash
$ cd {namespace.directory}
$ python3 -m spylt interface
$ python3 -m spylt build
$ python3 main.py
```
            """
        )
    )


def build(namespace: Namespace) -> None:
    """Compile Spylt backend module and Svelte code"""
    if not Path("src/App.py").exists():
        console.log(
            Markdown("𐄂 Could not find `src/App.py`. Are you in a Spylt project?")
        )
        sys.exit(1)

    start = time.time()
    with console.status("Transpiling backend code..."):
        app_context = run_path("src/App.py")
        app = [v for v in app_context.values() if isinstance(v, Module)][0]
        api_string = app.create_api()

        # There's some strange lines coming from module so trim it
        with open(namespace.py, "w", encoding="utf-8") as fh:
            fh.write("\n".join(api_string.split("\n")))
    end = time.time()

    console.log(f"✓ Backend code compiled in {end - start:.2f}s")

    start = time.time()
    with console.status("Compiling frontend code..."):
        pointer = find_pointer("src/App.svelte")
        linker_code = builder.create_link(pointer)
        html_output = builder.create_html(linker_code)
        app.create_interface()

        with open(namespace.html, "w", encoding="utf-8") as fh:
            fh.write(html_output)
    end = time.time()

    console.log(
        Markdown(
            f"""✓ Frontend code compiled in {end - start:.2f}s.

You can now run the app with `python3 {namespace.py}`"""
        )
    )


def interface(namespace: Namespace) -> None:
    """Create a JavaScript interface from a Spylt API"""
    start = time.time()

    with console.status("Creating interface from backend..."):
        if not Path("src/App.py").exists():
            console.log(
                Markdown("𐄂 Could not find `src/App.py`. Are you in a Spylt project?")
            )
            sys.exit(1)

        app_context = run_path("src/App.py")
        app = [v for v in app_context.values() if isinstance(v, Module)][0]
        interface_, suggest = app.create_interface()

    if suggest:
        with console.status(
            "ⓘ This project uses Pandas dataframes in some places. Installing dataframe-js..."
        ):
            os.system("npm install dataframe-js > /dev/null 2>/dev/null")
            os.system(
                "npm install --save-dev @types/dataframe-js > /dev/null 2>/dev/null"
            )

    with open(namespace.out, "w", encoding="utf-8") as fh:
        fh.write(interface_)
    end = time.time()

    console.log(
        Markdown(
            f"""Done in {end - start:.2f} s

`{namespace.out}` should now be available in your project"""
        )
    )


def create_cli() -> ArgumentParser:
    """Create an argparse CLI"""
    parser = ArgumentParser(
        prog="spylt",
        description=(
            "Spylt: A Python and Svelte framework which converts "
            "Python to API routes and Svelte to pre-rendered HTML"
        ),
    )

    subparsers = parser.add_subparsers()

    parser_new = subparsers.add_parser("new", help="Initialize a new Spylt project")
    parser_new.add_argument("directory", help="Directory to clone the project to")
    parser_new.set_defaults(func=new)

    parser_build = subparsers.add_parser(
        "build", help="Compile Spylt backend module and Svelte code"
    )
    parser_build.add_argument(
        "--html", help="Path to output compiled HTML", default="index.html"
    )
    parser_build.add_argument(
        "--py", help="Path to output compiled Python API", default="main.py"
    )
    parser_build.set_defaults(func=build)

    parser_interface = subparsers.add_parser(
        "interface", help="Create a JavaScript interface from a Spylt API"
    )
    parser_interface.add_argument(
        "--out", "-o", help="Path to output JavaScript interface", default="src/api.js"
    )
    parser_interface.set_defaults(func=interface)

    return parser
