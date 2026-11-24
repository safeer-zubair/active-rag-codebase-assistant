from src.llm_evaluator import evaluate_evidence


def main():
    evidence_bundle = {
        "original_query": "Where are HTTP redirects handled?",
        "retrieved_count": 1,
        "evidence": [
            {
                "rank": 1,
                "symbol": "SessionRedirectMixin.resolve_redirects",
                "file_path": "src/requests/sessions.py",
                "start_line": 186,
                "end_line": 307,
                "code": """
                def resolve_redirects(self, resp, req, ...):
                    # Handles redirect responses.
                    ...
                """
            }
        ]
    }

    print("Evaluating retrieved evidence...\n")

    result = evaluate_evidence(evidence_bundle)

    print("Assessment:")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()