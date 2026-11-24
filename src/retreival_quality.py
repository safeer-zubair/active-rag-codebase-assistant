from src.hybrid_retreival import tokenize_code

# The evidences collected from the query to send to quality assessment
def prepare_evidence(
    query: str,
    retrieved_results: list[dict],
) -> dict:

    evidence = []

    for rank, result in enumerate(retrieved_results, start=1):
        metadata = result["metadata"]

        evidence.append({
            "rank": rank,
            "symbol": (
                metadata.get("qualified_name")
                or metadata.get("symbol_name")
                or "__module__"
            ),
            "file_path": metadata["file_path"],
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "code": result["document"],
        })

    return {
        "original_query": query,
        "retrieved_count": len(evidence),
        "evidence": evidence,
    }

# Some of the words in the query should be removed to identify the keywords in the query
# Here for assessment, included some most commonly used words in a code retreieval query
STOP_WORDS = {
    "where", "what", "when", "why", "how",
    "does", "do", "is", "are", "the", "a",
    "an", "in", "on", "of", "to", "for",
    "and", "or", "with", "which", "that",
    "this", "it", "be", "by", "from",
}

# Rule based assessment of the retreived evidences
def assess_evidence(evidence_bundle: dict) -> dict:
    query = evidence_bundle["original_query"]
    evidence = evidence_bundle["evidence"]

    if not evidence:
        return {
            "status": "insufficient",
            "reason": "No evidence was retrieved.",
            "matched_terms": [],
            "query_terms": [],
            "overlap_ratio": 0.0, # The ratio of keywords overlapping from the retreived evidences with the keywords
        }

    query_terms = {
        token
        for token in tokenize_code(query)
        if token not in STOP_WORDS and len(token) > 1
    }

    if not query_terms: 
        return {
            "status": "weak",
            "reason": "The query contains no meaningful terms to compare.",
            "matched_terms": [],
            "query_terms": [],
            "overlap_ratio": 0.0,
        }

    evidence_terms = set()

    for item in evidence:
        searchable_text = f"{item['symbol']} {item['code']}"
        evidence_terms.update(tokenize_code(searchable_text))

    matched_terms = sorted(query_terms.intersection(evidence_terms))
    overlap_ratio = len(matched_terms) / len(query_terms)

    if not matched_terms:
        status = "weak"
        reason = "No meaningful query terms were found in the retrieved evidence"
    else:
        status = "candidate"
        reason = "Some meaningful query terms were found in the retrieved evidence"

    return {
        "status": status,
        "reason": reason,
        "matched_terms": matched_terms,
        "query_terms": sorted(query_terms),
        "overlap_ratio": overlap_ratio,
    }