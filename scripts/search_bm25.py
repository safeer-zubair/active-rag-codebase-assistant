from pathlib import Path

from src.vector_store import create_vector_store
from src.hybrid_retreival import build_bm25_index, search_bm25


def main():
    project_root = Path(__file__).resolve().parents[1]
    database_path = project_root / "data" / "chroma_db"

    print("Connecting to ChromaDB...")
    collection = create_vector_store(database_path)

    print("Building BM25 index...")
    index = build_bm25_index(collection)

    query = input("\nEnter your search query: ")

    if not query.strip():
        print("Please enter a valid query.")
        return

    results = search_bm25(index, query, top_k=10)

    print("\nBM25 Search Results:")

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print("\n" + "=" * 60)
        print(f"Rank: {rank}")
        print(f"BM25 Score: {result['score']:.4f}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"File: {metadata['file_path']}")
        print(f"Symbol: {metadata['qualified_name'] or metadata['symbol_name']}")
        print(f"Lines: {metadata['start_line']}-{metadata['end_line']}")

        print("\nCode preview:")
        print(result["document"][:500])

    print("\nSearch completed.")


if __name__ == "__main__":
    main()