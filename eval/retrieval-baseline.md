# Vector-only retrieval baseline

Embedding model:
sentence-transformers/all-MiniLM-L6-v2

Vector database:
ChromaDB

Chunking:
AST-aware chunking

Top-k:
10

Total indexed chunks:
349

## Diagnostic queries

### Query 1
HTTPAdapter.send

Expected symbol:
HTTPAdapter.send

Observed rank:
10

Observed similarity:
0.3843

### Query 2
The method that sends a prepared HTTP request using urllib3

Expected symbol:
HTTPAdapter.send

Observed rank:
Not found in top 10

### Query 3
Where does Session.request prepare an HTTP request before sending it?

Expected symbols:
Session.request
Session.prepare_request

Observed:
Session.request ranked 4
Session.prepare_request ranked 8