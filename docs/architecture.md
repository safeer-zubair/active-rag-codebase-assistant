## LLM-based Evidence Assessment

The system uses Groq GPT-OSS 20B to evaluate retrieved
code evidence.

The assessment receives:
- Original developer question
- Retrieved code
- Symbol names
- File paths
- Source line numbers

The LLM returns a structured assessment containing:
- Evidence sufficiency
- Relevance classification
- Assessment reasoning
- Missing information
- Refined retrieval query

### Assessment Validation

LLM responses are validated using deterministic Python rules.

Validation checks:
- Required fields
- Expected data types
- Valid relevance classifications
- Logical consistency between assessment fields

Invalid assessments raise validation errors and are not
accepted by the application.

The evaluation benchmark remains separate from runtime
assessment to prevent benchmark-label leakage.

# Active - retreival architecture
## Proposed json structure
```python
{
    "original_query": "...",
    "answer_evidence": [],
    "final_assessment": {},
    "retrieval_attempts": [
        {
            "attempt": 1,
            "query": "...",
            "retrieved_count": 10,
            "assessment": {}
        }
    ],
    "total_attempts": 1,
    "is_sufficient": True
}
```
This helps to look at how many attempts for retreiving the required evidences (maximum of 2 as proposed) and
recording each assessment retreivals with the modified query.