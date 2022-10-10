"""The CLI, I guess"""
import sys
from .builder import create_html, initialize, create_link

try:
    if sys.argv[1] == "init":
        initialize()
    elif sys.argv[1] == "html":
        create_html(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "link":
        create_link(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "api":
        pass
except IndexError as e:
    sys.exit("No such command exists (init, build, or link)")
