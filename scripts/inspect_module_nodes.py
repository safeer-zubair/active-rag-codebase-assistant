import ast
from pathlib import Path


def inspect_file(file_path: Path):
    source_code = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    tree = ast.parse(source_code)

    print("\n" + "=" * 80)
    print(f"FILE: {file_path}")
    print("=" * 80)

    for node in tree.body:
        start = node.lineno
        end = node.end_lineno

        if isinstance(node, ast.Import):
            description = "Import"

        elif isinstance(node, ast.ImportFrom):
            description = "ImportFrom"

        elif isinstance(node, ast.Assign):
            description = "Assignment"

        elif isinstance(node, ast.AnnAssign):
            description = "Annotated assignment"

        elif isinstance(node, ast.If):
            description = "If statement"

        elif isinstance(node, ast.Try):
            description = "Try statement"

        elif isinstance(node, ast.Expr):
            description = "Expression"

        elif isinstance(node, ast.ClassDef):
            description = f"Class: {node.name}"

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            description = f"Function: {node.name}"

        else:
            description = type(node).__name__

        print(f"{start:4}-{end:<4} | {description}")


def main():
    project_root = Path(__file__).resolve().parents[1]
    repo_path = project_root / "data" / "requests"

    target_files = [
        "src/requests/__init__.py",
        "src/requests/_types.py",
        "src/requests/models.py",
        "src/requests/status_codes.py",
        "src/requests/utils.py",
    ]

    for relative_path in target_files:
        inspect_file(repo_path / relative_path)


if __name__ == "__main__":
    main()