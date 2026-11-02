# Learning Notes

## 1. Repository Ingestion

### What is ingestion?

Ingestion is the process of loading source files
from a repository and preparing them for further
processing.

### Python concepts used

- pathlib: filesystem path handling
- rglob(): recursive file discovery
- read_text(): reading source files
- dictionaries: storing source code and metadata
- relative_to(): generating repository-relative paths

### Why do we exclude directories?

We exclude tests, documentation and generated
directories during our initial experiments to focus
on the main implementation code.

### Metadata collected

- File path
- Source code content
- Line count

### Implementation

src/ingest.py

### Next step

Transform source code into smaller chunks.

## 2. Automated Testing

### What is unit testing?

Unit testing verifies individual components of an
application independently.

### Testing framework

pytest

### Concepts learned

- Test functions
- Assertions
- pytest fixtures
- Temporary directories
- Exception testing

### Tests implemented

1. Recursive Python file discovery.
2. Excluded directory filtering.
3. Missing repository handling.
4. Invalid directory handling.
5. Source content and metadata verification.

### Execution command

python -m pytest -v

### Pytest Configuration

Created pytest.ini to control test discovery.

Configuration:

- testpaths = tests
- python_files = test_*.py

Reason:

The downloaded Requests repository contains its own
test suite. We only want to execute tests belonging
to our Active RAG project.

This prevents pytest from collecting unrelated
external repository tests.

## Fixed-Size Code Chunking

### What I learned

Chunking divides large source files into smaller sections that
can later be independently retrieved.

Our implementation uses line-based fixed-size chunking.

### Important concepts

- Chunk size: Maximum number of lines in a chunk.
- Overlap: Number of lines shared between adjacent chunks.
- Step size: Chunk size minus overlap.
- Metadata: Information that identifies the source of each chunk.

### Implementation

Created `src/chunking.py` with:

- chunk_python_file()
- chunk_python_files()

Each chunk stores:

- chunk_id
- file_path
- start_line
- end_line
- content

### Initial configuration

- Chunk size: 40 lines
- Overlap: 8 lines
- Step size: 32 lines

### Real repository inspection

Target repository: Requests

- Python files loaded: 20
- Chunks generated: 205

The ingestion rules exclude certain directories, so the number
of files loaded can differ from the total number of Python files
in the repository.

### Limitations

Fixed-size chunking can split functions and classes because
it does not understand Python syntax.

AST-aware chunking will be investigated in a later experiment.