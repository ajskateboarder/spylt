"""The CLI, I guess"""
import argparse
import sys
from runpy import run_path

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

    def build(self):
        if len(sys.argv) != 4:
            sys.exit(1)

        path = sys.argv[2]
        app_context = run_path(f"{path}.py")
        app = [v for v in app_context.values() if isinstance(v, Module)][0]
        api_string = app.create_api()

        # There's some strange lines coming from module so trim it
        with open("main.py", "w", encoding="utf-8") as fh:
            print(api_string.split("\n"))
            fh.write("\n".join(api_string.split("\n")[7:]))

        pointer = find_pointer(f"{path}.svelte")
        linker_code = builder.create_link(pointer)
        html_output = builder.create_html(linker_code)

        with open(sys.argv[3], "w", encoding="utf-8") as fh:
            fh.write(html_output)


CommandLine()
