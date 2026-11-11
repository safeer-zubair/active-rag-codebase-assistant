import re
from rank_bm25 import BM25Okapi

def tokenize_code(text: str) -> list[str]:
    # Split acronyms from normal words
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)

    # Split lowercase/digit characters from the uppercase characters
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)

    # Extract words and numbers and normalize them to lowercase
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return tokens

def build_bm25_index(collections):
    records = collections.get(
        include=["documents", "metadatas"]
    )

    ids = records["ids"]
    documents = records["documents"]
    metadatas = records["metadatas"]

    if not documents:
        raise ValueError("No documents found in the collection.")

    # Convert every document into a list of tokens
    tokenized_corpus = [
        tokenize_code(document)
        for document in documents
    ]

    # Build the BM25 index
    bm25 = BM25Okapi(tokenized_corpus)

    return {
        "bm25": bm25,
        "ids": ids,
        "documents": documents,
        "metadatas": metadatas,
    }


def search_bm25(index: dict, query: str, top_k: int = 5) -> list[dict]:
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    query_tokens = tokenize_code(query)

    if not query_tokens:
        return []

    # calculate BM25 relevance scores
    scores = index["bm25"].get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for i in ranked_indices[:top_k]:
        results.append({
            "chunk_id": index["ids"][i],
            "document": index["documents"][i],
            "metadata": index["metadatas"][i],
            "score": float(scores[i]),
        })

    return results

def reciprocal_rank_fusion(
        vector_results: list[dict],
        bm25_results: list[dict],
        k: int = 60
) -> list[dict]:
    if k <= 0:
        raise ValueError("k must be a positive integer.")

    fused_results = {}

    ranking_systems = [
        ("vector", vector_results),
        ("bm25", bm25_results)
    ]

    for system_name, results in ranking_systems:
        for rank, result in enumerate(results, start=1):
            chunk_id = result["chunk_id"]
            score = 1 / (rank + 1)

            if chunk_id not in fused_results:
                fused_results[chunk_id] = {
                    "chunk_id": chunk_id,
                    "document": result["document"],
                    "metadata": result["metadata"],
                    "rrf_score": 0.0,
                    "ranks": {},
                }

            entry = fused_results[chunk_id]

            entry["rrf_score"] += 1 / (k + rank)

            entry["ranks"][system_name] = rank

            if system_name == "vector":
                entry["vector_similarity"] = result.get(
                    "vector_similarity"
                )

            elif system_name == "bm25":
                entry["bm25_score"] = result.get("score")

    return sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )