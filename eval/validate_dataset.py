
import json
from pathlib import Path

from src.ingest import load_python_files
from src.ast_chunking import create_ast_chunks


def load_dataset(dataset_path: Path) -> list[dict]:
    questions = []

    with dataset_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                )

            if not isinstance(item, dict):
                raise ValueError(
                    f"Line {line_number} must contain a JSON object."
                )

            if not all(key in item for key in (
                "id", "question", "relevant_symbols"
            )):
                raise ValueError(
                    f"Missing required fields on line {line_number}."
                )

            if not isinstance(item["relevant_symbols"], list):
                raise ValueError(
                    f"relevant_symbols must be a list on line {line_number}."
                )

            questions.append(item)

    return questions


def main():
    project_root = Path(__file__).resolve().parents[1]

    dataset_path = project_root / "eval" / "questions.jsonl"
    repo_path = project_root / "data" / "requests"

    print("Loading evaluation dataset...")
    questions = load_dataset(dataset_path)

    print(f"Questions loaded: {len(questions)}")

    print("\nLoading repository...")
    loaded_files = load_python_files(repo_path)

    print(f"Python files loaded: {len(loaded_files)}")

    print("\nExtracting AST symbols...")

    available_symbols = set()

    for file_data in loaded_files:
        chunks = create_ast_chunks(file_data)

        for chunk in chunks:
            qualified_name = chunk.get("qualified_name")
            symbol_name = chunk.get("symbol_name")

            if qualified_name:
                available_symbols.add(qualified_name)

            if symbol_name:
                available_symbols.add(symbol_name)

    print(f"Available symbols: {len(available_symbols)}")

    print("\nValidating expected symbols...")

    all_valid = True
    seen_ids = set()

    for question in questions:
        question_id = question["id"]

        if question_id in seen_ids:
            print(f"Duplicate question ID: {question_id}")
            all_valid = False

        seen_ids.add(question_id)

        missing_symbols = [
            symbol
            for symbol in question["relevant_symbols"]
            if symbol not in available_symbols
        ]

        if missing_symbols:
            print(f"\n{question_id}: FAILED")
            print("Missing symbols:", missing_symbols)
            all_valid = False
        else:
            print(f"{question_id}: PASSED")

    print("\n" + "=" * 45)

    if all_valid:
        print("Dataset validation successful!")
        print(f"Validated questions: {len(questions)}")
    else:
        print("Dataset validation found problems.")
        print("Review the missing symbols and question IDs.")


if __name__ == "__main__":
    main()
