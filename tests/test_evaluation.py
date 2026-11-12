import pytest

from src.evaluation import (
    recall_at_k,
    reciprocal_rank,
    evaluate_query,
    aggregate_metrics,
    rank_at_one,
    aggregate_category_metrics,
)


def test_recall_at_3():
    retrieved = ["A", "B", "C", "D"]
    relevant = ["B", "D"]

    assert recall_at_k(retrieved, relevant, 3) == 0.5


def test_recall_at_5():
    retrieved = ["A", "B", "C", "D"]
    relevant = ["B", "D"]

    assert recall_at_k(retrieved, relevant, 5) == 1.0


def test_reciprocal_rank():
    retrieved = ["A", "B", "C"]
    relevant = ["C"]

    assert reciprocal_rank(retrieved, relevant) == pytest.approx(1 / 3)


def test_reciprocal_rank_when_not_found():
    retrieved = ["A", "B", "C"]
    relevant = ["D"]

    assert reciprocal_rank(retrieved, relevant) == 0.0


def test_evaluate_query():
    retrieved = ["A", "B", "C"]
    relevant = ["B"]

    result = evaluate_query(retrieved, relevant)

    assert result["recall@3"] == 1.0
    assert result["recall@5"] == 1.0
    assert result["mrr"] == 0.5
    assert result["first_relevant_rank"] == 2


def test_aggregate_metrics():
    results = [
        {
            "recall@3": 1.0,
            "recall@5": 1.0,
            "mrr": 1.0,
        },
        {
            "recall@3": 0.0,
            "recall@5": 1.0,
            "mrr": 0.5,
        },
    ]

    metrics = aggregate_metrics(results)

    assert metrics["recall@3"] == 0.5
    assert metrics["recall@5"] == 1.0
    assert metrics["mrr"] == 0.75


def test_invalid_k():
    with pytest.raises(ValueError):
        recall_at_k(["A"], ["A"], 0)


def test_empty_relevant_symbols():
    with pytest.raises(ValueError):
        reciprocal_rank(["A"], [])


def test_empty_aggregate_results():
    with pytest.raises(ValueError):
        aggregate_metrics([])


# Unified benchmarking dataset evalv
def test_rank_at_one_correct_symbol():
    assert rank_at_one(
        ["HTTPAdapter.send", "Session.send"],
        ["HTTPAdapter.send"],
    ) == 1.0


def test_rank_at_one_incorrect_symbol():
    assert rank_at_one(
        ["Session", "HTTPAdapter.send"],
        ["HTTPAdapter.send"],
    ) == 0.0


def test_rank_at_one_empty_results():
    assert rank_at_one(
        [],
        ["HTTPAdapter.send"],
    ) == 0.0


def test_category_aggregation():
    detailed_results = [
        {
            "category": "exact_identifier",
            "method": "wrrf",
            "recall@3": 1.0,
            "recall@5": 1.0,
            "mrr": 1.0,
            "rank@1": 1.0,
        },
        {
            "category": "exact_identifier",
            "method": "wrrf",
            "recall@3": 0.0,
            "recall@5": 1.0,
            "mrr": 0.5,
            "rank@1": 0.0,
        },
    ]

    results = aggregate_category_metrics(detailed_results)

    assert len(results) == 1
    assert results[0]["category"] == "exact_identifier"
    assert results[0]["method"] == "wrrf"
    assert results[0]["question_count"] == 2
    assert results[0]["rank@1"] == 0.5