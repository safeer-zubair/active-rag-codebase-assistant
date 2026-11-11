
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
    }
