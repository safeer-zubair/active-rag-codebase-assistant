
from pathlib import Path

from src.active import (
    load_retrieval_resources,
    retrieve_hybrid,
)


def main():
    print("Loading retrieval resources...")

    resources = load_retrieval_resources(Path.cwd())

    query = "Where are HTTP redirects handled in the Requests library?"

    print(f"\nQuestion: {query}")
    print("\nPerforming hybrid retrieval...")

    results = retrieve_hybrid(
        query=query,
        model=resources["model"],
        collection=resources["collection"],
        bm25_index=resources["bm25_index"],
        top_k=10,
    )

    print(f"\nRetrieved: {len(results)} chunks")

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]

        symbol = (
            metadata.get("qualified_name")
            or metadata.get("symbol_name")
            or "__module__"
        )

        print("\n" + "=" * 60)
        print(f"Rank: {rank}")
        print(f"Symbol: {symbol}")
        print(f"File: {metadata['file_path']}")
        print(
            f"Lines: {metadata['start_line']}-"
            f"{metadata['end_line']}"
        )
        print(f"RRF Score: {result['rrf_score']:.5f}")
        print(f"Ranking sources: {result['ranks']}")


if __name__ == "__main__":
    main()