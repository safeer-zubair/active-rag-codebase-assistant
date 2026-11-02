def chunk_python_file(
        file_data: dict,
        chunk_size: int = 40,
        overlap: int = 8
) -> list[dict]:
    """
    Split the code into chunks by lines (chunk size and the overlappung is experimental, it can be changed).
    Each chunk will contain the original path and the line numbers.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overalp cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")

    content = file_data["content"]
    file_path = file_data["file_path"]

    lines = content.splitlines()

    chunks = []

    step_size = chunk_size - overlap

    start_index = 0

    while start_index < len(lines):
        end_index = min(
            start_index + chunk_size,
            len(lines)
        )

        chunk_lines = lines[start_index:end_index]

        chunk = {
            "chunk_id": (
                f"{file_path}:"
                f"{start_index + 1}-{end_index}"
            ),
            "file_path": file_path,
            "start_line": start_index + 1,
            "end_line": end_index,
            "content": "\n".join(chunk_lines),
        }

        chunks.append(chunk)

        if end_index == len(lines):
            break

        start_index += step_size

    return chunks

def chunk_python_files(
    loaded_files: list[dict],
    chunk_size: int = 40,
    overlap: int = 8,
) -> list[dict]:
    """
    Chunk multiple Python files and combine their chunks
    """

    all_chunks = []

    for file_data in loaded_files:
        file_chunks = chunk_python_file(
            file_data,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        all_chunks.extend(file_chunks)

    return all_chunks