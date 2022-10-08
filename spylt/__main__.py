"""The CLI, I guess"""
import sys
from .builder import build, initialize, create_link

if sys.argv[1] == "init":
    initialize()
elif sys.argv[1] == "build":
    build(sys.argv[2])
elif sys.argv[1] == "link":
    create_link(sys.argv[2], sys.argv[3])
