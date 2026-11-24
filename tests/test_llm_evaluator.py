import pytest

from src.llm_evaluator import validate_assessment


def make_assessment(
    is_sufficient=True,
    relevance="relevant",
    missing_information=None,
    refined_query="",
):
    return {
        "is_sufficient": is_sufficient,
        "relevance": relevance,
        "reason": "Test assessment reason.",
        "missing_information": missing_information or [],
        "refined_query": refined_query,
    }


def test_valid_sufficient_assessment():
    assessment = make_assessment()

    result = validate_assessment(assessment)

    assert result == assessment


def test_valid_partially_relevant_assessment():
    assessment = make_assessment(
        is_sufficient=False,
        relevance="partially_relevant",
        missing_information=["Authentication handling"],
        refined_query="How is authentication rebuilt after redirects?",
    )

    result = validate_assessment(assessment)

    assert result == assessment


def test_valid_irrelevant_assessment():
    assessment = make_assessment(
        is_sufficient=False,
        relevance="irrelevant",
        missing_information=["Redirect handling"],
        refined_query="Where are HTTP redirects handled?",
    )

    result = validate_assessment(assessment)

    assert result == assessment


def test_reject_contradictory_sufficient_assessment():
    assessment = make_assessment(
        is_sufficient=True,
        relevance="irrelevant",
        missing_information=["Redirect handling"],
        refined_query="Find redirect handling",
    )

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_insufficient_assessment_without_missing_information():
    assessment = make_assessment(
        is_sufficient=False,
        relevance="partially_relevant",
        refined_query="Find redirect handling",
    )

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_insufficient_assessment_without_refined_query():
    assessment = make_assessment(
        is_sufficient=False,
        relevance="partially_relevant",
        missing_information=["Redirect handling"],
    )

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_invalid_relevance():
    assessment = make_assessment(
        relevance="maybe",
    )

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_missing_fields():
    assessment = make_assessment()
    del assessment["reason"]

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_invalid_field_type():
    assessment = make_assessment(
        is_sufficient="true",
    )

    with pytest.raises(ValueError):
        validate_assessment(assessment)


def test_reject_empty_reason():
    assessment = make_assessment()
    assessment["reason"] = "   "

    with pytest.raises(ValueError):
        validate_assessment(assessment)