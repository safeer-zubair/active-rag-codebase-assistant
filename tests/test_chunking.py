import pytest

from src.chunking import (
    chunk_python_file,
    chunk_python_files,
)


def test_short_file_creates_one_chunk():
    file_data = {
        "file_path": "example.py",
        "content": "x = 10\ny = 20",
    }

    chunks = chunk_python_file(file_data)

    assert len(chunks) == 1
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 2
    assert chunks[0]["content"] == "x = 10\ny = 20"


def test_file_is_split_into_multiple_chunks():
    content = "\n".join(
        f"line {i}" for i in range(1, 101)
    )

    file_data = {
        "file_path": "example.py",
        "content": content,
    }

    chunks = chunk_python_file(
        file_data,
        chunk_size=40,
        overlap=8,
    )

    assert len(chunks) == 3

    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 40

    assert chunks[1]["start_line"] == 33
    assert chunks[1]["end_line"] == 72

    assert chunks[2]["start_line"] == 65
    assert chunks[2]["end_line"] == 100


def test_overlap_preserves_shared_lines():
    content = "\n".join(
        f"line {i}" for i in range(1, 81)
    )

    file_data = {
        "file_path": "example.py",
        "content": content,
    }

    chunks = chunk_python_file(
        file_data,
        chunk_size=40,
        overlap=8,
    )

    first_chunk_lines = chunks[0]["content"].splitlines()
    second_chunk_lines = chunks[1]["content"].splitlines()

    assert first_chunk_lines[-8:] == second_chunk_lines[:8]


def test_empty_file_returns_no_chunks():
    file_data = {
        "file_path": "empty.py",
        "content": "",
    }

    chunks = chunk_python_file(file_data)

    assert chunks == []


def test_invalid_chunk_size_raises_error():
    file_data = {
        "file_path": "example.py",
        "content": "x = 10",
    }

    with pytest.raises(ValueError):
        chunk_python_file(file_data, chunk_size=0)


def test_overlap_must_be_smaller_than_chunk_size():
    file_data = {
        "file_path": "example.py",
        "content": "x = 10",
    }

    with pytest.raises(ValueError):
        chunk_python_file(
            file_data,
            chunk_size=10,
            overlap=10,
        )


def test_multiple_files_are_chunked_together():
    loaded_files = [
        {
            "file_path": "first.py",
            "content": "x = 10",
        },
        {
            "file_path": "second.py",
            "content": "y = 20",
        },
    ]

    chunks = chunk_python_files(loaded_files)

    assert len(chunks) == 2
    assert chunks[0]["file_path"] == "first.py"
    assert chunks[1]["file_path"] == "second.py"

def test_exact_chunk_size_creates_one_chunk():
    content = "\n".join(
        f"line {i}" for i in range(1, 41)
    )

    file_data = {
        "file_path": "example.py",
        "content": content,
    }

    chunks = chunk_python_file(
        file_data,
        chunk_size=40,
        overlap=8,
    )

    assert len(chunks) == 1
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 40