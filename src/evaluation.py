def recall_at_k(
    retrieved_symbols: list[str],
    relevant_symbols: list[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not relevant_symbols:
        raise ValueError("relevant_symbols cannot be empty")

    retrieved_top_k = set(retrieved_symbols[:k])
    relevant = set(relevant_symbols)

    found = retrieved_top_k.intersection(relevant)

    return len(found) / len(relevant)


def reciprocal_rank(
    retrieved_symbols: list[str],
    relevant_symbols: list[str],
) -> float:
    if not relevant_symbols:
        raise ValueError("relevant_symbols cannot be empty")

    relevant = set(relevant_symbols)

    for rank, symbol in enumerate(retrieved_symbols, start=1):
        if symbol in relevant:
            return 1 / rank

    return 0.0


def rank_at_one(
    retrieved_symbols: list[str],
    relevant_symbols: list[str],
) -> float:
    if not relevant_symbols:
        raise ValueError("relevant_symbols cannot be empty")

    if not retrieved_symbols:
        return 0.0

    return float(retrieved_symbols[0] in set(relevant_symbols))


def evaluate_query(
    retrieved_symbols: list[str],
    relevant_symbols: list[str],
) -> dict:

    first_relevant_rank = next(
        (
            rank
            for rank, symbol in enumerate(retrieved_symbols, start=1)
            if symbol in set(relevant_symbols)
        ),
        None,
    )

    return {
        "recall@3": recall_at_k(
            retrieved_symbols, relevant_symbols, k=3
        ),
        "recall@5": recall_at_k(
            retrieved_symbols, relevant_symbols, k=5
        ),
        "mrr": reciprocal_rank(
            retrieved_symbols, relevant_symbols
        ),
        "rank@1": rank_at_one(
            retrieved_symbols, relevant_symbols
        ),
        "first_relevant_rank": first_relevant_rank,
    }


def aggregate_metrics(query_results: list[dict]) -> dict:
    if not query_results:
        raise ValueError("query_results cannot be empty")

    number_of_queries = len(query_results)

    return {
        "recall@3": sum(
            result["recall@3"] for result in query_results
        ) / number_of_queries,

        "recall@5": sum(
            result["recall@5"] for result in query_results
        ) / number_of_queries,

        "mrr": sum(
            result["mrr"] for result in query_results
        ) / number_of_queries,

        "rank@1": sum(
            result.get("rank@1", 0.0) for result in query_results
        ) / number_of_queries,
    }


def aggregate_category_metrics(
    detailed_results: list[dict],
) -> list[dict]:

    grouped_results = {}

    for result in detailed_results:
        category = result["category"]
        method = result["method"]

        key = (category, method)

        if key not in grouped_results:
            grouped_results[key] = []

        grouped_results[key].append(result)

    category_summaries = []

    for (category, method), results in grouped_results.items():
        metrics = aggregate_metrics(results)

        category_summaries.append({
            "category": category,
            "method": method,
            "question_count": len(results),
            **metrics,
        })

    return category_summaries