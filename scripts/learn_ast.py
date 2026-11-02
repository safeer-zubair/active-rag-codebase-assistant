import ast


source_code = """
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello {self.name}"


def calculate_total(a, b):
    return a + b
"""


tree = ast.parse(source_code)

print("AST structure:\n")

for node in ast.walk(tree):

    if isinstance(node, ast.ClassDef):
        print(
            f"CLASS: {node.name} "
            f"| Lines: {node.lineno}-{node.end_lineno}"
        )

    elif isinstance(node, ast.FunctionDef):
        print(
            f"FUNCTION: {node.name} "
            f"| Lines: {node.lineno}-{node.end_lineno}"
        )