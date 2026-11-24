from src.llm_client import generate_response

def main():
    prompt = """
    Explain what is a python function in two sentences.
    """

    print("Sending request to Groq client...")

    response = generate_response(prompt)

    print("\nGroq response:")
    print(response)

if __name__ == "__main__":
    main()