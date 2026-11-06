from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.ingest import load_python_files
from src.ast_chunking import create_ast_chunks
from src.vector_store import create_vector_store, add_chunks


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    project_root = Path(__file__).resolve().parents[1]

    # 1. Locate the source repository
    repo_path = project_root / "data" / "requests"

    # 2. Load Python files
    print("Loading Python files...")

    loaded_files = load_python_files(repo_path)

    print(f"Files loaded: {len(loaded_files)}")

    # 3. Convert source files into AST chunks
    print("\nCreating AST chunks...")

    all_chunks = []

    for file_data in loaded_files:
        file_chunks = create_ast_chunks(file_data)
        all_chunks.extend(file_chunks)

    print(f"AST chunks created: {len(all_chunks)}")

    if not all_chunks:
        print("No chunks found. Nothing to index.")
        return

    # 4. Load the embedding model
    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    # 5. Prepare documents for embedding
    documents = [
        (
            chunk.get("qualified_name")
            or chunk.get("symbol_name")
            or "__module__"
        )
        + "\n"
        + chunk["content"]
        for chunk in all_chunks
    ]

    # 6. Generate embeddings
    print("\nGenerating embeddings...")

    embeddings = model.encode(
        documents,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    print("Embedding shape:", embeddings.shape)

    # 7. Connect to persistent ChromaDB
    print("\nConnecting to ChromaDB...")

    database_path = project_root / "data" / "chroma_db"

    collection = create_vector_store(database_path)

    # 8. Store chunks, embeddings and metadata
    print("\nIndexing chunks...")

    add_chunks(
        collection=collection,
        chunks=all_chunks,
        embeddings=embeddings,
    )

    # 9. Verify indexing
    print("\nIndexing completed!")

    print("Collection:", collection.name)
    print("Total stored records:", collection.count())


if __name__ == "__main__":
    main()