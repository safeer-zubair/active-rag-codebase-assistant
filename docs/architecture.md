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