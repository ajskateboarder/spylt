"""AST Node visitor to check for non-local imports (requests, cmath)"""
import ast


def check_imports(source):
    tree = ast.parse(source)
    print(ast.dump(tree))

    imports = MainLevelImports()
    imports.visit(tree)
    
    return imports.level_imports


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
