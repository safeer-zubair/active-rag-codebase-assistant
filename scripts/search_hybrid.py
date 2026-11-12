from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.vector_store import create_vector_store, search_collection
from src.hybrid_retreival import build_bm25_index, search_bm25, reciprocal_rank_fusion, search_exact_symbol

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 10

def main():
    project_root = Path(__file__).resolve().parents[1]
    database_path = project_root / "data" / "chroma_db"

    print("Loading the embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("\nConnecting to ChromaDB...")
    collection = create_vector_store(database_path)
    print("Indexed chunks:", collection.count())

    print("\nBuilding BM25 index...")
    bm25_index = build_bm25_index(collection)
    print("Total BM25 indexed documents:", len(bm25_index["documents"]))

    query = input("\nAsk a question about the repository: ")

    if not query.strip():
        print("Please enter a question.")
        return

    # 1. Generate the query embedding
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # 2. Run vector search
    print("\nRunning vector search...")
    vector_raw = search_collection(
        collection,
        query_embedding,
        top_k=TOP_K,
    )

    
    vector_results = []

    vector_ids = vector_raw["ids"][0]
    vector_documents = vector_raw["documents"][0]
    vector_metadatas = vector_raw["metadatas"][0]
    vector_distances = vector_raw["distances"][0]

    for i in range(len(vector_ids)):
        vector_results.append({
            "chunk_id": vector_ids[i],
            "document": vector_documents[i],
            "metadata": vector_metadatas[i],
            "vector_similarity": 1 - vector_distances[i],
        })


    # 3. Run BM25 search
    print("\nRunning BM25 search...")
    bm25_results = search_bm25(
        bm25_index,
        query,
        top_k=TOP_K,
    )

    exact_results = search_exact_symbol(
        bm25_index,
        query,
        top_k=10,
    )

    # Debugging snippet (Data type mismatch issue)
    # print("\nDEBUG - Vector result ID:")
    # print(vector_results[0]["chunk_id"])
    # print(type(vector_results[0]["chunk_id"]))

    # print("\nDEBUG - BM25 result ID:")
    # print(bm25_results[0]["chunk_id"])
    # print(type(bm25_results[0]["chunk_id"]))

    # 4. Combine both rankings usin RRF
    print("\nCombining rankings using Reciprocal Rank Fusion...")
    hybrid_results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        exact_results=exact_results,
        k=60,
    )

    # Printing the results before the final display for debugging purposes
    print(f"\nVector results: {len(vector_results)}")
    print(f"BM25 results: {len(bm25_results)}")
    print(f"Exact matches: {len(exact_results)}")
    print(f"Fused results: {len(hybrid_results)}")

    # 5. Display the final rankings
    print("\n" + "=" * 65)
    print("HYBRID SEARCH RESULTS")
    print("=" * 65)

    for position, result in enumerate(hybrid_results[:TOP_K], start=1):
        metadata = result["metadata"]

        symbol = (
            metadata["qualified_name"]
            or metadata["symbol_name"]
            or "__module__"
        )

        ranks = result["ranks"]

        vector_rank = ranks.get("vector", "—")
        bm25_rank = ranks.get("bm25", "—")

        print("\n" + "-" * 65)
        print(f"Final rank: {position}")
        print(f"Ranks: {result['ranks']}")
        print(f"Exact match: {result.get('exact_match', False)}")
        print(f"RRF score: {result['rrf_score']:.5f}")
        print(f"Vector rank: {vector_rank}")
        print(f"BM25 rank: {bm25_rank}")
        print(f"File: {metadata['file_path']}")
        print(f"Symbol: {symbol}")
        print(
            f"Lines: {metadata['start_line']}-"
            f"{metadata['end_line']}"
        )

        print("\nCode preview:")
        print(result["document"][:1000])

    print("\nHybrid search completed!")


if __name__ == "__main__":
    main()


