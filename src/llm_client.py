import os
import json

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def create_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Your GROQ key is not found in the .env file, check it."
            )

    return Groq(api_key=api_key)

def get_model_name() -> str:
    model_name = os.getenv("GROQ_MODEL")

    if not model_name:
        raise ValueError(
            "Groq model was not found, check the .env file"
        )

    return model_name

def generate_response(prompt: str) -> str:
    client = create_groq_client()
    model_name = get_model_name()

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.2,
        max_completion_tokens=1200,
    )

    return response.choices[0].message.content


import json


def generate_structured_response(
    system_prompt: str,
    user_prompt: str,
    schema: dict,
) -> dict:

    client = create_groq_client()
    model_name = get_model_name()

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
        max_completion_tokens=1000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "retrieval_quality_assessment",
                "strict": True,
                "schema": schema,
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    return json.loads(content)