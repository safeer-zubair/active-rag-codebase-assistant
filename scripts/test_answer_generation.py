
from pathlib import Path

from src.active import (
    load_retrieval_resources,
    active_retrieve,
)

from src.generate import generate_grounded_answer


def main():
    resources = load_retrieval_resources(Path.cwd())

    query = "Where are HTTP redirects handled in the Requests library?"

    print("Running active retrieval...")

    retrieval_result = active_retrieve(
        original_query=query,
        resources=resources,
        top_k=10,
        max_retries=2,
    )

    print(f"Retrieval attempts: {retrieval_result['total_attempts']}")

    if not retrieval_result["is_sufficient"]:
        print("\nInsufficient evidence.")
        print(retrieval_result["final_assessment"]["reason"])
        return

    print("\nEvidence sufficient. Generating answer...")

    answer_result = generate_grounded_answer(
        original_query=query,
        evidence=retrieval_result["answer_evidence"],
        assessment=retrieval_result["final_assessment"],
    )

    print("\n" + "=" * 65)
    print("GENERATED ANSWER")
    print("=" * 65)

    print(answer_result["answer"])

    print("\n" + "=" * 65)
    print("CITATION INFORMATION")
    print("=" * 65)

    print(f"Citations used: {answer_result['citation_count']}")

    for evidence_id, source in answer_result["citations"].items():
        print(f"{evidence_id} -> {source}")


if __name__ == "__main__":
    main()