
from pathlib import Path

from src.active import (
    load_retrieval_resources,
    active_retrieve,
)


def main():
    print("Loading retrieval resources...")

    resources = load_retrieval_resources(Path.cwd())

    query = "Where are HTTP redirects handled in the Requests library?"

    print(f"\nOriginal question: {query}")
    print("\nStarting active retrieval...")

    result = active_retrieve(
        original_query=query,
        resources=resources,
        top_k=10,
        max_retries=2,
    )

    print("\n" + "=" * 65)
    print("ACTIVE RETRIEVAL REPORT")
    print("=" * 65)

    print(f"\nOriginal question: {result['original_query']}")
    print(f"Total attempts: {result['total_attempts']}")
    print(f"Evidence sufficient: {result['is_sufficient']}")

    for attempt in result["retrieval_attempts"]:
        print("\n" + "-" * 65)
        print(f"ATTEMPT {attempt['attempt']}")
        print("-" * 65)

        print(f"Search query: {attempt['search_query']}")
        print(f"Retrieved this attempt: {attempt['retrieved_count']}")
        print(
            "Unique accumulated evidence: "
            f"{attempt['total_unique_evidence']}"
        )

        print("\nDeterministic assessment:")
        print(attempt["deterministic_assessment"])

        print("\nLLM assessment:")
        print(attempt["llm_assessment"])

    print("\n" + "=" * 65)
    print("FINAL ASSESSMENT")
    print("=" * 65)
    print(result["final_assessment"])

    print("\n" + "=" * 65)
    print("ACCUMULATED EVIDENCE")
    print("=" * 65)

    for item in result["answer_evidence"]:
        metadata = item["metadata"]

        print(
            f"\n{metadata.get('qualified_name') or '__module__'}"
            f" | {metadata['file_path']}"
            f":{metadata['start_line']}-{metadata['end_line']}"
        )


if __name__ == "__main__":
    main()