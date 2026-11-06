from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.ast_chunking import create_ast_chunks


def main():
    # 1. Locate the Requests source file
    project_root = Path(__file__).resolve().parents[1]

    source_path = (
        project_root
        / "data"
        / "requests"
        / "src"
        / "requests"
        / "sessions.py"
    )

    source_code = source_path.read_text(encoding="utf-8")

    # 2. Generate AST chunks from the source file
    file_data = {
        "file_path": "src/requests/sessions.py",
        "content": source_code,
    }

    chunks = create_ast_chunks(file_data)

    # 3. Select four methods for our experiment
    selected_names = {
        "resolve_redirects",
        "rebuild_auth",
        "request",
        "send",
    }

    selected_chunks = [
        chunk
        for chunk in chunks
        if chunk["symbol_type"] == "method"
        and chunk["symbol_name"] in selected_names
    ]

    print(f"Selected code chunks: {len(selected_chunks)}")

    # 4. Prepare the text that will be embedded
    documents = [
        f"{chunk['qualified_name']}\n{chunk['content']}"
        for chunk in selected_chunks
    ]

    # 5. Load the embedding model
    print("\nLoading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # 6. Convert code chunks into embeddings
    print("\nGenerating code embeddings...")

    code_embeddings = model.encode(
        documents,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    print("Code embedding shape:", code_embeddings.shape)

    # 7. Inspect one actual embedding
    print("\nFirst 10 values of the first embedding:")
    print(code_embeddings[0][:10])

    # 8. Embed a natural-language question
    query = "Where are redirects followed after a server responds with a redirect status?"

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    print("\nQuery embedding shape:", query_embedding.shape)

    # 9. Calculate cosine similarity
    # Because both embeddings are normalized,
    # their dot product equals cosine similarity
    similarities = code_embeddings @ query_embedding

    # 10. Rank the chunks by similarity
    ranked_results = sorted(
        zip(similarities, selected_chunks),
        key=lambda item: item[0],
        reverse=True,
    )

    print("\nSearch results:")

    for score, chunk in ranked_results:
        print(
            f"\nSimilarity: {score:.4f}"
            f"\nMethod: {chunk['qualified_name']}"
            f"\nFile: {chunk['file_path']}"
            f"\nLines: {chunk['start_line']}-{chunk['end_line']}"
        )


if __name__ == "__main__":
    main()