
import csv
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.vector_store import create_vector_store, search_collection
from src.hybrid_retreival import (
    build_bm25_index,
    search_bm25,
    reciprocal_rank_fusion,
)
from src.evaluation import evaluate_query, aggregate_metrics


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 10


def load_questions(dataset_path: Path) -> list[dict]:
    questions = []

    with dataset_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                questions.append(json.loads(line))

    return questions


def convert_vector_results(raw_results: dict) -> list[dict]:
    results = []

    ids = raw_results["ids"][0]
    documents = raw_results["documents"][0]
    metadatas = raw_results["metadatas"][0]
    distances = raw_results["distances"][0]

    for i in range(len(ids)):
        results.append({
            "chunk_id": ids[i],
            "document": documents[i],
            "metadata": metadatas[i],
            "vector_similarity": 1 - distances[i],
        })

    return results


def extract_symbols(results: list[dict]) -> list[str]:
    symbols = []

    for result in results:
        metadata = result["metadata"]

        symbol = (
            metadata.get("qualified_name")
            or metadata.get("symbol_name")
        )

        if symbol:
            symbols.append(symbol)

    return symbols


def evaluate_retriever(
    questions: list[dict],
    model,
    collection,
    bm25_index,
    retriever_name: str,
) -> tuple[list[dict], dict]:

    query_results = []
    detailed_results = []

    for question in questions:
        question_id = question["id"]
        query = question["question"]
        relevant_symbols = question["relevant_symbols"]

        print(f"Evaluating {question_id}: {query}")

        vector_results = []
        bm25_results = []

        if retriever_name in ("vector", "hybrid"):
            query_embedding = model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            raw_vector_results = search_collection(
                collection,
                query_embedding,
                top_k=TOP_K,
            )

            vector_results = convert_vector_results(
                raw_vector_results
            )

        if retriever_name in ("bm25", "hybrid"):
            bm25_results = search_bm25(
                bm25_index,
                query,
                top_k=TOP_K,
            )

        if retriever_name == "vector":
            final_results = vector_results

        elif retriever_name == "bm25":
            final_results = bm25_results

        else:
            final_results = reciprocal_rank_fusion(
                vector_results,
                bm25_results,
                k=60,
            )

        retrieved_symbols = extract_symbols(
            final_results[:TOP_K]
        )

        metrics = evaluate_query(
            retrieved_symbols,
            relevant_symbols,
        )

        query_results.append(metrics)

        detailed_results.append({
            "question_id": question_id,
            "method": retriever_name,
            **metrics,
        })

    summary = aggregate_metrics(query_results)

    return detailed_results, summary


def main():
    project_root = Path(__file__).resolve().parents[1]

    dataset_path = project_root / "eval" / "questions.jsonl"
    database_path = project_root / "data" / "chroma_db"

    results_path = project_root / "eval" / "results.csv"
    summary_path = project_root / "eval" / "summary.csv"

    print("Loading evaluation questions...")
    questions = load_questions(dataset_path)
    print(f"Questions: {len(questions)}")

    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("\nConnecting to ChromaDB...")
    collection = create_vector_store(database_path)
    print("Indexed chunks:", collection.count())

    print("\nBuilding BM25 index...")
    bm25_index = build_bm25_index(collection)

    all_detailed_results = []
    all_summaries = []

    for method in ("vector", "bm25", "hybrid"):
        print(f"\n{'=' * 50}")
        print(f"Evaluating: {method.upper()}")
        print("=" * 50)

        detailed, summary = evaluate_retriever(
            questions,
            model,
            collection,
            bm25_index,
            method,
        )

        all_detailed_results.extend(detailed)

        all_summaries.append({
            "method": method,
            **summary,
        })

    detailed_fields = [
        "question_id",
        "method",
        "recall@3",
        "recall@5",
        "mrr",
        "first_relevant_rank",
    ]

    summary_fields = [
        "method",
        "recall@3",
        "recall@5",
        "mrr",
    ]

    with results_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=detailed_fields
        )
        writer.writeheader()
        writer.writerows(all_detailed_results)

    with summary_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=summary_fields
        )
        writer.writeheader()
        writer.writerows(all_summaries)

    print("\n" + "=" * 50)
    print("FINAL EVALUATION")
    print("=" * 50)

    for result in all_summaries:
        print(f"\nMethod: {result['method'].upper()}")
        print(f"Recall@3: {result['recall@3']:.4f}")
        print(f"Recall@5: {result['recall@5']:.4f}")
        print(f"MRR:      {result['mrr']:.4f}")

    print("\nDetailed results saved to:", results_path)
    print("Summary saved to:", summary_path)


if __name__ == "__main__":
    main()