
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


# Using metadata retreiving the code snippet when a qualified symbol is given
# Eg: "Where is HTTPAdapter.send implemented?" should return the code snippet for HTTPAdapter.send

from src.hybrid_retreival import search_exact_symbol

def make_symbol_index():
    return {
        "ids": ["chunk_1", "chunk_2", "chunk_3"],
        "documents": [
            "HTTPAdapter.send implementation",
            "Session.get_adapter implementation",
            "Session.send implementation",
        ],
        "metadatas": [
            {
                "qualified_name": "HTTPAdapter.send",
                "symbol_name": "send",
                "file_path": "src/requests/adapters.py",
                "start_line": 634,
                "end_line": 748,
            },
            {
                "qualified_name": "Session.get_adapter",
                "symbol_name": "get_adapter",
                "file_path": "src/requests/sessions.py",
                "start_line": 870,
                "end_line": 881,
            },
            {
                "qualified_name": "Session.send",
                "symbol_name": "send",
                "file_path": "src/requests/sessions.py",
                "start_line": 752,
                "end_line": 829,
            },
        ],
    }


def test_exact_qualified_symbol_is_found():
    index = make_symbol_index()

    results = search_exact_symbol(
        index,
        "Where is HTTPAdapter.send implemented?",
    )

    assert len(results) == 1
    assert results[0]["metadata"]["qualified_name"] == "HTTPAdapter.send"


def test_exact_symbol_preserves_source_metadata():
    index = make_symbol_index()

    results = search_exact_symbol(
        index,
        "Explain Session.get_adapter",
    )

    assert results[0]["metadata"]["file_path"] == "src/requests/sessions.py"
    assert results[0]["metadata"]["start_line"] == 870
    assert results[0]["metadata"]["end_line"] == 881


def test_natural_language_query_returns_no_exact_match():
    index = make_symbol_index()

    results = search_exact_symbol(
        index,
        "How does Requests send HTTP requests?",
    )

    assert results == []


def test_nonexistent_symbol_returns_empty_list():
    index = make_symbol_index()

    results = search_exact_symbol(
        index,
        "Where is HTTPAdapter.delete implemented?",
    )

    assert results == []


def test_exact_search_respects_top_k():
    index = make_symbol_index()

    results = search_exact_symbol(
        index,
        "Where is Session.send implemented?",
        top_k=1,
    )

    assert len(results) <= 1


def test_invalid_top_k_raises_error():
    index = make_symbol_index()

    with pytest.raises(ValueError):
        search_exact_symbol(index, "HTTPAdapter.send", top_k=0)


def test_exact_results_are_included_in_fusion():
    vector_results = [
        {**make_result("A"), "vector_similarity": 0.9},
    ]

    bm25_results = [
        {**make_result("B"), "score": 8.0},
    ]

    exact_results = [
        {**make_result("C"), "exact_match": True},
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        exact_results=exact_results,
    )

    result_ids = {item["chunk_id"] for item in results}

    assert result_ids == {"A", "B", "C"}


def test_exact_match_rank_is_recorded():
    exact_results = [
        {**make_result("A"), "exact_match": True},
    ]

    results = reciprocal_rank_fusion(
        [],
        [],
        exact_results=exact_results,
    )

    assert results[0]["ranks"]["exact"] == 1
    assert results[0]["exact_match"] is True


# Test after implementing metadata retrieval for exact matches,
# ensuring that chunks found by all three systems get their scores combined correctly.

# def test_chunk_found_by_all_three_systems_gets_three_scores():
#     vector_results = [
#         {**make_result("A"), "vector_similarity": 0.9},
#     ]

#     bm25_results = [
#         {**make_result("A"), "score": 8.0},
#     ]

#     exact_results = [
#         {**make_result("A"), "exact_match": True},
#     ]

#     results = reciprocal_rank_fusion(
#         vector_results,
#         bm25_results,
#         exact_results=exact_results,
#     )

#     assert len(results) == 1

#     assert results[0]["rrf_score"] == pytest.approx(
#         3 / 61
#     )

#     assert results[0]["ranks"] == {
#         "vector": 1,
#         "bm25": 1,
#         "exact": 1,
#     }

# Tests for the weighted reciprocal rank fusion (highest weight is given for the exact match)

def test_weighted_rrf_prioritizes_exact_matches():
    vector_results = [
        make_result("A"),
        make_result("B"),
    ]

    bm25_results = [
        make_result("A"),
        make_result("B"),
    ]

    exact_results = [
        make_result("B"),
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        exact_results=exact_results,
        exact_weight=3.0,
    )

    assert results[0]["chunk_id"] == "B"


def test_weighted_rrf_uses_custom_weights():
    vector_results = [make_result("A")]
    bm25_results = []
    exact_results = [make_result("B")]

    results = reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        exact_results=exact_results,
        vector_weight=1.0,
        exact_weight=5.0,
    )

    assert results[0]["chunk_id"] == "B"


def test_weighted_rrf_rejects_negative_weights():
    try:
        reciprocal_rank_fusion(
            [],
            [],
            vector_weight=-1.0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_weighted_rrf_rejects_all_zero_weights():
    try:
        reciprocal_rank_fusion(
            [],
            [],
            vector_weight=0.0,
            bm25_weight=0.0,
            exact_weight=0.0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
