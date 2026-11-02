from pathlib import Path

from src.ingest import load_python_files
from src.ast_chunking import create_ast_chunks


def main():
    project_root = Path(__file__).resolve().parents[1]
    repo_path = project_root / "data" / "requests"

    loaded_files = load_python_files(repo_path)

    target_names = {
        "_ValidatedRequest",
        "BaseRequestKwargs",
        "RequestKwargs",
        "GetKwargs",
        "PostKwargs",
        "DataKwargs",
    }

    found_names = set()

    for file_data in loaded_files:
        if file_data["file_path"].endswith("_types.py"):
            chunks = create_ast_chunks(file_data)

            for chunk in chunks:
                if chunk["symbol_name"] in target_names:
                    found_names.add(chunk["symbol_name"])

                    print(
                        f"{chunk['symbol_type']:16} "
                        f"{chunk['qualified_name']:25} "
                        f"lines {chunk['start_line']}-{chunk['end_line']}"
                    )
                    print(
                        f"Control context: {chunk['control_context']}"
                    )
                    print("-" * 60)

    missing_names = target_names - found_names

    print(f"\nExpected definitions: {len(target_names)}")
    print(f"Found definitions: {len(found_names)}")

    if missing_names:
        print(f"Missing: {sorted(missing_names)}")
    else:
        print("All six nested classes were successfully chunked.")


if __name__ == "__main__":
    main()