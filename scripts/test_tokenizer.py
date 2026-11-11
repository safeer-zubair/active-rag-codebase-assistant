from src.hybrid_retreival import tokenize_code

examples = [
    "HTTPAdapter.send",
    "prepare_request",
    "resolveRedirects",
    "get_connection_with_tls_context",
    "Session.prepare_request",
]

for example in examples:
    tokens = tokenize_code(example)
    print(f"Input: {example} -> Tokens: {tokens}")