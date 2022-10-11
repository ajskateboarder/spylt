from pprint import pprint
import ast


def main():
    with open("main.py", "r") as source:
        tree = ast.parse(source.read())

        imports = MainLevelImports()
        imports.visit(tree)
        print(imports.level_imports)


class MainLevelImports(ast.NodeVisitor):
    def __init__(self) -> None:
        self.level_imports = []

    def visit_Import(self, node):
        if not hasattr(node, "level"):
            for alias in node.names:
                self.level_imports.append(alias.name)

    def visit_ImportFrom(self, node):
        if not hasattr(node, "level"):
            for alias in node.names:
                self.level_imports.append(alias.name)


if __name__ == "__main__":
    main()
