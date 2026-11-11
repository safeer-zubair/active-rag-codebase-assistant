from pathlib import Path

from src.vector_store import create_vector_store
from src.hybrid_retreival import build_bm25_index

def main():
    project_root = Path(__file__).resolve().parents[1]

    database_path = project_root / "data" / "chroma_db"

    print("Connecting to chroma db...")

    collection = create_vector_store(database_path)

    print("Stored records:", collection.count())

    print("\nBuilding BM25 index...")

    index = build_bm25_index(collection)

    print("\nBM25 index built successfully.")
    print("Number of documents in the index:", len(index["documents"]))
    print("Number of IDs in the index:", len(index["ids"]))
    print("Number of metadatas in the index:", len(index["metadatas"]))

if __name__ == "__main__":
    main()