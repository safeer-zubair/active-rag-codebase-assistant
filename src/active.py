from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.hybrid_retreival import(
    build_bm25_index,
    reciprocal_rank_fusion,
    search_bm25,
    search_exact_symbol,
)

from src.retreival_quality import(
    prepare_evidence,
    assess_evidence,
)

from src.llm_evaluator import evaluate_evidence
from src.vector_store import create_vector_store, search_collection

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 10
DEFAULT_MAX_RETRIES = 2

def load_retrieval_resources(project_root: Path):
    """
    This loads the embedding model, ChromaDB collection and the
    in memory BM25 index.

    This loads once when the application is loaded.
    """

    model = SentenceTransformer(MODEL_NAME)

    database_path = project_root / "data" / "chroma_db"

    collection = create_vector_store(database_path)

    if collection.count() == 0:
        raise ValueError(
            "The vector databse is empty, index a repository before asking a question."
        )

    bm25_index = build_bm25_index(collection)

    return{
        "model": model,
        "collection": collection,
        "bm25_index": bm25_index,
    }


def retrieve_hybrid(
    query: str,
    model,
    collection,
    bm25_index: dict,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict]:
    """
    Retrieve code using vector search, BM25 and
    exact-symbol matching, then combine the rankings
    """

    if not query.strip():
        raise ValueError("The search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # 1. Convert the query into an embedding
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    # 2. Perform vector search
    vector_response = search_collection(
        collection=collection,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    # 3. Convert ChromaDB's nested response into
    # the flat result format expected by RRF
    vector_results = []

    for i, chunk_id in enumerate(vector_response["ids"][0]):
        distance = vector_response["distances"][0][i]

        vector_results.append({
            "chunk_id": chunk_id,
            "document": vector_response["documents"][0][i],
            "metadata": vector_response["metadatas"][0][i],
            "vector_similarity": 1 - distance,
        })

    # 4. Perform keyword retrieval
    bm25_results = search_bm25(
        index=bm25_index,
        query=query,
        top_k=top_k,
    )

    # 5. Find exact qualified identifiers
    exact_results = search_exact_symbol(
        index=bm25_index,
        query=query,
        top_k=top_k,
    )

    # 6. Combine all three rankings
    fused_results = reciprocal_rank_fusion(
        vector_results=vector_results,
        bm25_results=bm25_results,
        exact_results=exact_results,
        vector_weight=1.0,
        bm25_weight=1.0,
        exact_weight=3.0,
    )

    return fused_results[:top_k]


def active_retrieve(
    original_query: str,
    resources: dict,
    top_k: int = DEFAULT_TOP_K,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict:
    """
    Run the active retrieval loop.

    The system retrieves evidence, evaluates it,
    refines the query when necessary and retries.

    max_retries is limited to two, meaning at most
    three total retrieval attempts.
    """

    if not original_query.strip():
        raise ValueError("The original question cannot be empty.")

    if not 0 <= max_retries <= DEFAULT_MAX_RETRIES:
        raise ValueError("max_retries must be between 0 and 2.")

    model = resources["model"]
    collection = resources["collection"]
    bm25_index = resources["bm25_index"]

    current_query = original_query

    # Keep evidence from every attempt.
    collected_evidence = {}
    retrieval_attempts = []

    final_assessment = None
    is_sufficient = False

    for attempt_number in range(1, max_retries + 2):

        # A. Retrieve using the current search query
        retrieved_results = retrieve_hybrid(
            query=current_query,
            model=model,
            collection=collection,
            bm25_index=bm25_index,
            top_k=top_k,
        )

        # B. Preserve new evidence without duplicates
        for result in retrieved_results:
            chunk_id = result["chunk_id"]

            if chunk_id not in collected_evidence:
                collected_evidence[chunk_id] = result

        combined_results = list(collected_evidence.values())

        # C. Prepare all accumulated evidence against
        # the developer's ORIGINAL question
        evidence_bundle = prepare_evidence(
            query=original_query,
            retrieved_results=combined_results,
        )

        # D. Calculate deterministic retrieval diagnostics
        deterministic_assessment = assess_evidence(
            evidence_bundle
        )

        # E. Ask the LLM whether the evidence is sufficient
        final_assessment = evaluate_evidence(
            evidence_bundle
        )

        # F. Record what happened during this attempt
        retrieval_attempts.append({
            "attempt": attempt_number,
            "search_query": current_query,
            "retrieved_count": len(retrieved_results),
            "total_unique_evidence": len(combined_results),
            "deterministic_assessment": deterministic_assessment,
            "llm_assessment": final_assessment,
        })

        # G. Stop if sufficient evidence has been found
        if final_assessment["is_sufficient"]:
            is_sufficient = True
            break

        # H. Stop if we have used all allowed attempts
        if attempt_number == max_retries + 1:
            break

        # I. Refine the search query
        refined_query = final_assessment["refined_query"].strip()

        # Prevent repeated searches with the same query
        if refined_query.casefold() == current_query.casefold():
            break

        current_query = refined_query

    return {
        "original_query": original_query,
        "answer_evidence": list(collected_evidence.values()),
        "final_assessment": final_assessment,
        "retrieval_attempts": retrieval_attempts,
        "total_attempts": len(retrieval_attempts),
        "is_sufficient": is_sufficient,
    }
