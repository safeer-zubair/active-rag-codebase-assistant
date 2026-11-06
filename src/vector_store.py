from pathlib import Path

import chromadb

import json


COLLECTION_NAME = "active_rag_code_chunks"


def create_vector_store(
    persist_directory: Path,
    collection_name: str = COLLECTION_NAME,
):
    """
    Create or connect to a persistent ChromaDB collection
    """

    client = chromadb.PersistentClient(
        path=str(persist_directory)
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def add_chunks(
    collection,
    chunks: list[dict],
    embeddings,
):
    """
    Store code chunks, embeddings and metadata
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match "
            "the number of embeddings."
        )

    if not chunks:
        return

    ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    documents = []

    for chunk in chunks:
        symbol_name = (
            chunk.get("qualified_name")
            or chunk.get("symbol_name")
            or "__module__"
        )

        document = f"{symbol_name}\n{chunk['content']}"
        documents.append(document)

    metadatas = []

    for chunk in chunks:
        metadata = {
            "file_path": chunk["file_path"],
            "symbol_name": chunk.get("symbol_name") or "",
            "qualified_name": chunk.get("qualified_name") or "",
            "symbol_type": chunk["symbol_type"],
            "start_line": int(chunk["start_line"]),
            "end_line": int(chunk["end_line"]),
            "control_context": json.dumps(
                chunk.get("control_context") or []
            ),
        }

        if chunk.get("parent_symbol"):
            metadata["parent_symbol"] = chunk["parent_symbol"]

        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )


def search_collection(
    collection,
    query_embedding,
    top_k: int = 5,
):
    """
    Search for code chunks similar to a query embedding
    """

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    return collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )