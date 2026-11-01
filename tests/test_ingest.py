
from pathlib import Path

import pytest

from src.ingest import (
    discover_python_files,
    load_python_files,
)


def create_file(path: Path, content: str = ""):
    """Helper function to create test files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discover_python_files(tmp_path):
    """Find Python files recursively."""

    create_file(tmp_path / "main.py", "print('hello')")
    create_file(tmp_path / "src" / "app.py", "print('app')")

    files = discover_python_files(tmp_path)

    relative_paths = {
        file.relative_to(tmp_path).as_posix()
        for file in files
    }

    assert relative_paths == {
        "main.py",
        "src/app.py",
    }


def test_excluded_directories(tmp_path):
    """Ignore directories listed in EXCLUDED_DIRS."""

    create_file(tmp_path / "src" / "app.py")
    create_file(tmp_path / "tests" / "test_app.py")
    create_file(tmp_path / "docs" / "example.py")
    create_file(tmp_path / "__pycache__" / "cached.py")

    files = discover_python_files(tmp_path)

    relative_paths = {
        file.relative_to(tmp_path).as_posix()
        for file in files
    }

    assert relative_paths == {
        "src/app.py",
    }


def test_missing_repository():
    """Raise an error if the repository does not exist."""

    invalid_path = Path("non_existing_repository")

    with pytest.raises(FileNotFoundError):
        discover_python_files(invalid_path)


def test_repository_path_is_not_directory(tmp_path):
    """Raise an error if the supplied path is a file."""

    file_path = tmp_path / "example.txt"
    file_path.write_text("hello", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        discover_python_files(file_path)


def test_load_python_files_metadata(tmp_path):
    """Verify loaded content and metadata."""

    source_code = "def hello():\n    return 'world'\n"

    create_file(
        tmp_path / "src" / "hello.py",
        source_code,
    )

    loaded_files = load_python_files(tmp_path)

    assert len(loaded_files) == 1

    file_data = loaded_files[0]

    assert file_data["file_path"] == "src/hello.py"
    assert file_data["content"] == source_code
    assert file_data["line_count"] == 2
