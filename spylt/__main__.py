"""The CLI, I guess"""
import argparse
import sys
from .builder import create_html, initialize, create_link

class CommandLine:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Spylt CLI',
            usage='''spylt <command> [<args>]

Commands:
   init     Initialize a new Spylt project
   html     Compile Svelte code imported to Python
   api      Compile Python functions into APIs

''')

        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(1)
        getattr(self, args.command)()

    def init(self):
        initialize()

    def html(self):
        try:
            create_link(sys.argv[2], "./main.js")
            create_html(sys.argv[3], "./main.js")
        except IndexError:
            sys.exit("Required arguments: <path to py>:<app object> <path to html>")

CommandLine()
