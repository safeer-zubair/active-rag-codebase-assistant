from pathlib import Path

from src.ingest import load_python_files
from src.chunking import chunk_python_files


def main():
    project_root = Path(__file__).resolve().parents[1]
    repo_path = project_root / "data" / "requests"

    print("Loading Python files...")

    loaded_files = load_python_files(repo_path)

    print(f"Python files loaded: {len(loaded_files)}")

    print("\nCreating chunks...")

    chunks = chunk_python_files(
        loaded_files,
        chunk_size=40,
        overlap=8,
    )

    print(f"Total chunks created: {len(chunks)}")

    print("\nChunks per file:")

    chunks_per_file = {}

    for chunk in chunks:
        file_path = chunk["file_path"]

        chunks_per_file[file_path] = (
            chunks_per_file.get(file_path, 0) + 1
        )

    for file_path, count in sorted(chunks_per_file.items()):
        print(f"{file_path}: {count} chunks")

    print("\nExample chunks from sessions.py:")

    for chunk in chunks:
        if chunk["file_path"].endswith("sessions.py"):
            print("\n" + "=" * 60)
            print(f"Chunk ID: {chunk['chunk_id']}")
            print(f"Lines: {chunk['start_line']}-{chunk['end_line']}")
            print("=" * 60)
            print(chunk["content"][:500])

            break

    print("\nAll chunks from sessions.py:")

    for chunk in chunks:
        if chunk["file_path"].endswith("sessions.py"):
            print(
                f"{chunk['start_line']}-{chunk['end_line']}"
            )


if __name__ == "__main__":
    main()

    