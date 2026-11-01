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