from spylt.imports import check_imports

with open("./main.py", encoding="utf-8") as fh:
    print(check_imports(fh.read()))
