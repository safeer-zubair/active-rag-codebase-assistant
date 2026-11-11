
import pytest

from src.hybrid_retreival import reciprocal_rank_fusion


def make_result(chunk_id):
    return {
        "chunk_id": chunk_id,
        "document": f"Code for {chunk_id}",
        "metadata": {"file_path": "example.py"},
    }


def test_chunk_ranked_by_both_systems_gets_combined_score():
    vector_results = [
        {**make_result("A"), "vector_similarity": 0.9},
        {**make_result("B"), "vector_similarity": 0.8},
    ]

    bm25_results = [
        {**make_result("B"), "score": 8.0},
        {**make_result("A"), "score": 7.0},
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
    )

    scores = {item["chunk_id"]: item["rrf_score"] for item in results}

    expected_a = (1 / 61) + (1 / 62)
    expected_b = (1 / 62) + (1 / 61)

    assert scores["A"] == pytest.approx(expected_a)
    assert scores["B"] == pytest.approx(expected_b)


def test_chunk_missing_from_one_system_is_still_included():
    vector_results = [
        {**make_result("A"), "vector_similarity": 0.9},
    ]

    bm25_results = [
        {**make_result("B"), "score": 8.0},
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
    )

    assert len(results) == 2


def test_fusion_records_original_ranks():
    vector_results = [
        {**make_result("A"), "vector_similarity": 0.9},
    ]

    bm25_results = [
        {**make_result("A"), "score": 8.0},
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
    )

    assert results[0]["ranks"] == {
        "vector": 1,
        "bm25": 1,
    }


def test_invalid_k_raises_error():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], [], k=0)
