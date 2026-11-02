from pathlib import Path

from src.ingest import load_python_files
from src.ast_chunking import create_ast_chunks


def main():
    project_root = Path(__file__).resolve().parents[1]
    repo_path = project_root / "data" / "requests"

    loaded_files = load_python_files(repo_path)

    all_chunks = []

    for file_data in loaded_files:
        try:
            chunks = create_ast_chunks(file_data)
            all_chunks.extend(chunks)

        except SyntaxError as error:
            print(
                f"Could not parse {file_data['file_path']}: "
                f"{error}"
            )

    print(f"Python files loaded: {len(loaded_files)}")
    print(f"AST chunks created: {len(all_chunks)}")

    print("\nChunk types:")

    chunk_types = {}

    for chunk in all_chunks:
        symbol_type = chunk["symbol_type"]
        chunk_types[symbol_type] = (
            chunk_types.get(symbol_type, 0) + 1
        )

    for symbol_type, count in sorted(chunk_types.items()):
        print(f"{symbol_type}: {count}")

    print("\nDefinitions in sessions.py:")

    for chunk in all_chunks:
        if chunk["file_path"].endswith("sessions.py"):
            print(
                f"{chunk['symbol_type']:10} "
                f"{chunk['symbol_name']:25} "
                f"{chunk['start_line']}-{chunk['end_line']}"
            )

            
    print("\nAST chunk size statistics:")

    chunk_sizes = [
        len(chunk["content"].splitlines())
        for chunk in all_chunks
    ]

    print(f"Total chunks: {len(chunk_sizes)}")
    print(f"Smallest chunk: {min(chunk_sizes)} lines")
    print(f"Largest chunk: {max(chunk_sizes)} lines")
    print(
        f"Average chunk size: "
        f"{sum(chunk_sizes) / len(chunk_sizes):.2f} lines"
    )

    oversized_chunks = [
        chunk for chunk in all_chunks
        if len(chunk["content"].splitlines()) > 100
    ]

    print("\nOversized chunks by type:")

    oversized_by_type = {}

    for chunk in oversized_chunks:
        symbol_type = chunk["symbol_type"]

        oversized_by_type[symbol_type] = (
            oversized_by_type.get(symbol_type, 0) + 1
        )

    for symbol_type, count in sorted(oversized_by_type.items()):
        print(f"{symbol_type}: {count}")


    print("\nOversized functions and methods:")

    for chunk in oversized_chunks:
        if chunk["symbol_type"] in {"function", "method"}:
            size = len(chunk["content"].splitlines())

            print(
                f"{chunk['symbol_type']:10} "
                f"{chunk['symbol_name']:30} "
                f"{size:4} lines "
                f"| {chunk['file_path']}"
            )

    print(
        f"\nChunks exceeding 100 lines: "
        f"{len(oversized_chunks)}"
    )

    print("\nLargest 10 chunks:")

    largest_chunks = sorted(
        all_chunks,
        key=lambda chunk: len(
            chunk["content"].splitlines()
        ),
        reverse=True,
    )[:10]

    for chunk in largest_chunks:
        size = len(chunk["content"].splitlines())

        print(
            f"{chunk['symbol_type']:10} "
            f"{chunk['symbol_name']:25} "
            f"{size:4} lines "
            f"| {chunk['file_path']}"
        )

    print("\nOversized chunk details:")

    for chunk in oversized_chunks:
        size = len(chunk["content"].splitlines())

        print(
            f"{chunk['symbol_type']:10} "
            f"{chunk['symbol_name']:30} "
            f"{size:4} lines "
            f"| {chunk['start_line']}-{chunk['end_line']} "
            f"| {chunk['file_path']}"
        )

    print("\nOversized module chunk previews:")

    for chunk in oversized_chunks:
        if chunk["symbol_type"] == "module":
            print("\n" + "=" * 70)
            print(f"File: {chunk['file_path']}")
            print(
                f"Lines: {chunk['start_line']}-"
                f"{chunk['end_line']}"
            )
            print("=" * 70)

            print("\n".join(chunk["content"].splitlines()[:15]))


if __name__ == "__main__":
    main()