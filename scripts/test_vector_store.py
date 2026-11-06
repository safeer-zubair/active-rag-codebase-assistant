from pathlib import Path

from src.vector_store import create_vector_store


def main():
    project_root = Path(__file__).resolve().parents[1]

    database_path = project_root / "data" / "chroma_db"

    collection = create_vector_store(database_path)

    print("ChromaDB connected successfully!")
    print("Collection:", collection.name)
    print("Existing records:", collection.count())


if __name__ == "__main__":
    main()