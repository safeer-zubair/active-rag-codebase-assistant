import csv
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.vector_store import create_vector_store, search_collection
from src.hybrid_retreival import (
    build_bm25_index,
    search_bm25,
    search_exact_symbol,
    reciprocal_rank_fusion,
)

from src.evaluation import (
    evaluate_query,
    aggregate_metrics,
    aggregate_category_metrics,
)

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
        exact_results = []

        # 1. Vector retreival
        if retriever_name in ("vector", "rrf", "rrf_equal", "wrrf"):
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


        # 2. BM25 retreival
        if retriever_name in ("bm25", "rrf", "rrf_equal", "wrrf"):
            bm25_results = search_bm25(
                bm25_index,
                query,
                top_k=TOP_K,
            )

        # 3. Exact-symbol retrieval
        if retriever_name in ("rrf_equal", "wrrf"):
            exact_results = search_exact_symbol(
                bm25_index,
                query,
                top_k=TOP_K,
            )

            print(
                f"{question_id} | Exact matches: {len(exact_results)}"
            )

            for result in exact_results:
                print(
                    "  ",
                    result["metadata"].get("qualified_name"),
                    result["metadata"].get("file_path"),
                    result["metadata"].get("start_line"),
                )

        # 4. Select final retreival results
        if retriever_name == "vector":
            final_results = vector_results

        elif retriever_name == "bm25":
            final_results = bm25_results

        elif retriever_name == "rrf":
            final_results = reciprocal_rank_fusion(
                vector_results,
                bm25_results,
                k=60
            )

        elif retriever_name == "rrf_equal":
            final_results = reciprocal_rank_fusion(
                vector_results,
                bm25_results,
                exact_results=exact_results,
                k=60,
                vector_weight=1.0,
                bm25_weight=1.0,
                exact_weight=1.0,
            )

        elif retriever_name == "wrrf":
            final_results = reciprocal_rank_fusion(
                vector_results,
                bm25_results,
                exact_results=exact_results,
                k=60,
                vector_weight=1.0,
                bm25_weight=1.0,
                exact_weight=3.0,
            ) 

        else:
            raise ValueError(
                f"Unknown retreiver: {retriever_name}"
            )

        # 5. Evaluate retreived symbols
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
            "category": question["category"],
            "method": retriever_name,
            **metrics,
        })

    summary = aggregate_metrics(query_results)

    return detailed_results, summary


def main():
    project_root = Path(__file__).resolve().parents[1]

    dataset_path = project_root / "eval" / "benchmark_questions.jsonl"
    database_path = project_root / "data" / "chroma_db"

    results_path = project_root / "eval" / "results.csv"
    summary_path = project_root / "eval" / "summary.csv"
    category_summary_path = project_root / "eval" / "category_summary.csv"

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

    methods = (
        "vector",
        "bm25",
        "rrf",
        "rrf_equal",
        "wrrf",
    )

    for method in methods:
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

    # Generate category-level summaries
    category_summaries = aggregate_category_metrics(
        all_detailed_results
    )

    detailed_fields = [
        "question_id",
        "category",
        "method",
        "recall@3",
        "recall@5",
        "mrr",
        "rank@1",
        "first_relevant_rank",
    ]

    summary_fields = [
        "method",
        "recall@3",
        "recall@5",
        "mrr",
        "rank@1",
    ]

    category_fields = [
        "category",
        "method",
        "question_count",
        "recall@3",
        "recall@5",
        "mrr",
        "rank@1",
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

    with category_summary_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=category_fields
        )
        writer.writeheader()
        writer.writerows(category_summaries)

    print("\n" + "=" * 50)
    print("FINAL EVALUATION")
    print("=" * 50)

    for result in all_summaries:
        print(f"\nMethod: {result['method'].upper()}")
        print(f"Recall@3: {result['recall@3']:.4f}")
        print(f"Recall@5: {result['recall@5']:.4f}")
        print(f"MRR:      {result['mrr']:.4f}")
        print(f"Rank@1:   {result['rank@1']:.4f}")

    print("\nDetailed results saved to:", results_path)
    print("Summary saved to:", summary_path)
    print("Category summary saved to:", category_summary_path)


if __name__ == "__main__":
    main()