"""The CLI, I guess"""
import argparse
import sys
from runpy import run_path
from time import time

from . import builder
from .cli import template
from .helpers import find_pointer
from .module import Module


class CommandLine:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=(
                "Spylt: A Python and Svelte framework which converts "
                "Python to API routes and Svelte to pre-rendered HTML"
            ),
            usage="""spylt <command> [<args>]

Available commands:
   new:      Initialize a new Spylt project
   html:     Compile Svelte code to HTML
   build:    Compile Spylt backend module and Svelte code
""",
        )

        parser.add_argument("command", help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print("Unrecognized command")
            parser.print_help()
            sys.exit(1)
        getattr(self, args.command)()

    def new(self):
        template(sys.argv[2])

    def html(self):
        try:
            start = time()
            print(f"Compiling {sys.argv[2]} to {sys.argv[3]}...")
            pointer = find_pointer(sys.argv[2])
            builder.create_link(pointer, sys.argv[3])
            builder.create_html(sys.argv[3], sys.argv[3])
            end = time()
            print(f"Finished in {end - start:.2f}")
        except IndexError:
            sys.exit("Required arguments: <path to svelte> <path to html>")

    def build(self):
        path = sys.argv[2]
        app_context = run_path(f"{path}.py")
        app = [v for v in app_context.values() if isinstance(v, Module)][0]
        api_string = app.create_api(get_string=True)

        # There's some strange lines coming from module so trim it
        with open("main.py", "w", encoding="utf-8") as fh:
            print(api_string.split("\n"))
            fh.write("\n".join(api_string.split("\n")[7:]))

        pointer = find_pointer(f"{path}.svelte")
        builder.create_link(pointer, "main.js")
        builder.create_html("index.html", "main.js")


CommandLine()
