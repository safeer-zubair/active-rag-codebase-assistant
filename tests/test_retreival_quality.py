
from src.retreival_quality import prepare_evidence, assess_evidence

# test for the evidence retrieval
def test_prepare_evidence():
    query = "Where does Session.send send requests?"

    retrieved_results = [
        {
            "chunk_id": "sessions.py:752-829",
            "document": "def send(self, request, **kwargs):\n    pass",
            "metadata": {
                "qualified_name": "Session.send",
                "symbol_name": "send",
                "file_path": "src/requests/sessions.py",
                "start_line": 752,
                "end_line": 829,
            },
            "rrf_score": 0.05,
        }
    ]

    result = prepare_evidence(query, retrieved_results)

    assert result["original_query"] == query
    assert result["retrieved_count"] == 1

    evidence = result["evidence"][0]

    assert evidence["rank"] == 1
    assert evidence["symbol"] == "Session.send"
    assert evidence["file_path"] == "src/requests/sessions.py"
    assert evidence["start_line"] == 752
    assert evidence["end_line"] == 829

# test for quality assessment (rule based quality assessment)
def test_assess_evidence_with_no_results():
    evidence_bundle = {
        "original_query": "Where are redirects handled?",
        "evidence": [],
    }

    result = assess_evidence(evidence_bundle)

    assert result["status"] == "insufficient"
    assert result["overlap_ratio"] == 0.0


def test_assess_evidence_with_keyword_overlap():
    evidence_bundle = {
        "original_query": "Where does Session.send send requests?",
        "evidence": [
            {
                "symbol": "Session.send",
                "code": "def send(self, request, **kwargs): pass",
            }
        ],
    }

    result = assess_evidence(evidence_bundle)

    assert result["status"] == "candidate"
    assert "send" in result["matched_terms"]
    assert result["overlap_ratio"] > 0.0


def test_assess_evidence_without_keyword_overlap():
    evidence_bundle = {
        "original_query": "Where are redirects handled?",
        "evidence": [
            {
                "symbol": "Request.prepare",
                "code": "def prepare(self): pass",
            }
        ],
    }

    result = assess_evidence(evidence_bundle)

    assert result["status"] == "weak"
    assert result["matched_terms"] == []