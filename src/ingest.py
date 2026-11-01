# selecting the suitable files before chunking

from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "tests",
    "docs",
    "build",
    "dist",
    "vendor",
    "node_modules",
}

def discover_python_files(repo_path: Path) -> list[Path]:
    """
    Find Python files inside a repository.

    Excludes files located inside the directories listed in EXCLUDED_DIRS.
    """

    if not repo_path.exists():
        raise FileNotFoundError(
            f"Expected a directory: {repo_path}"
        )

    if not repo_path.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {repo_path}"
        )

    python_files = []

    for file_path in repo_path.rglob("*py"):
        relative_path = file_path.relative_to(repo_path)

        if any(
            part in EXCLUDED_DIRS
            for part in relative_path.parts[:-1]
        ):
            continue

        python_files.append(file_path)

    return sorted(python_files)

def load_python_files(repo_path: Path) -> list[dict]:  
    """
    Read discovered Python files and collect their metadata.

    Each result contains:
    - file_path: relative path inside the repository
    - content: complete source code
    - line_count: number of source lines
    """

    python_files = discover_python_files(repo_path)

    loaded_files = []

    for file_path in python_files:

        content = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        relative_path = file_path.relative_to(
        repo_path
        ).as_posix()

        file_data = {
        "file_path": relative_path,
        "content": content,
        "line_count": len(content.splitlines()),
        }

        loaded_files.append(file_data)

    return loaded_files

def main():
    # Locate the Requests repository relative to this file.
    project_root = Path(__file__).resolve().parents[1]
    repo_path = project_root / "data" / "requests"

    print("Starting repository ingestion...")

    loaded_files = load_python_files(repo_path)

    print(f"\nTotal Python files loaded: {len(loaded_files)}")

    print("\nFirst five loaded files:")

    for file_data in loaded_files[:5]:
        print(
            f"- {file_data['file_path']} "
            f"({file_data['line_count']} lines)"
        )

    print("\nRepository ingestion completed.")


if __name__ == "__main__":
    main()
