import ast
from pathlib import Path


def inspect_nested_definitions(node, depth=0):
    indent = "    " * depth

    if isinstance(node, ast.ClassDef):
        print(f"{indent}Class: {node.name}")

    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        print(f"{indent}Function: {node.name}")

    # Inspect all child AST nodes recursively
    for child in ast.iter_child_nodes(node):
        inspect_nested_definitions(child, depth + 1)


def main():
    project_root = Path(__file__).resolve().parents[1]

    file_path = (
        project_root
        / "data"
        / "requests"
        / "src"
        / "requests"
        / "_types.py"
    )

    source_code = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(source_code)

    print("Definitions discovered in _types.py:\n")

    inspect_nested_definitions(tree)


if __name__ == "__main__":
    main()