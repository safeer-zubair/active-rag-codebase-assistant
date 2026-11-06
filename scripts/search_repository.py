from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.vector_store import create_vector_store, search_collection


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    project_root = Path(__file__).resolve().parents[1]

    # 1. Load the same embedding model used during indexing
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    # 2. Connect to the existing vector database
    database_path = project_root / "data" / "chroma_db"

    collection = create_vector_store(database_path)

    print(f"Indexed chunks: {collection.count()}")

    get_answer = True

    while(get_answer):
        # 3. Get a question from the user.
        query = input("\nAsk a question about the repository: ")

        if not query.strip():
            print("Please enter a question.")
            return

        if query == "exit":
            print("Exiting the search.")
            return
        
        # 4. Convert the question into an embedding
        query_embedding = model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # 5. Retrieve the five most similar chunks
        results = search_collection(
            collection=collection,
            query_embedding=query_embedding,
            top_k=10,
        )

        # 6. Display the results
        print("\nSearch results:")

        for index in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][index]
            document = results["documents"][0][index]
            distance = results["distances"][0][index]

            similarity = 1 - distance

            print("\n" + "=" * 60)

            print(f"Result: {index + 1}")
            print(f"Similarity: {similarity:.4f}")
            print(f"File: {metadata['file_path']}")
            print(
                f"Symbol: {metadata['qualified_name'] or metadata['symbol_name']}"
            )
            print(
                f"Lines: {metadata['start_line']}-{metadata['end_line']}"
            )

            print("\nCode preview:")
            print(document[:1000])

        print("\nSearch completed.")


if __name__ == "__main__":
    main()