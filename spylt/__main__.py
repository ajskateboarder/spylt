"""The CLI, I guess"""
import argparse
from time import time
import sys

from .builder import create_html, template, create_link
from .helpers import find_pointer


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
   html:     Transpile Svelte code imported to Python
   api:      Convert Python functions into APIs
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
            s = time()
            print(f"Compiling {sys.argv[2]} to {sys.argv[3]}...")
            pointer = find_pointer(sys.argv[2])
            create_link(pointer, sys.argv[3])
            create_html(sys.argv[3], sys.argv[3])
            e = time()
            print(f"Finished in {e - s:.2f}")
        except IndexError:
            sys.exit("Required arguments: <path to py>:<app object> <path to html>")


CommandLine()
