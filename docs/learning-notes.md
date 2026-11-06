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

## AST-aware chunking: recursive definition discovery

### What I implemented

Used Python's `ast` module to identify classes, functions, methods, and nested functions in source code.

The AST visitor now recursively traverses child nodes instead of inspecting only direct class and function bodies.

### Why recursive traversal matters

Python definitions can appear inside control-flow statements such as:

- `if`
- `try`
- `for`
- `while`
- `with`

A visitor that only checks direct children of the module, classes, and functions can miss definitions inside these structures.

### Metadata improvements

Each definition stores:

- Symbol name
- Qualified name
- Symbol type
- Parent symbol
- Start and end line
- Enclosing control-flow context

Control-flow context is stored separately from the qualified name because a condition such as `TYPE_CHECKING` is not part of a definition's lexical name.

### Real repository validation

Tested against the Requests repository:

- Python files loaded: 20
- AST chunks created: 349
- Classes: 52
- Functions: 83
- Methods: 177
- Nested functions: 8
- Module chunks: 29

Verified that six classes inside the `if TYPE_CHECKING` block in `src/requests/_types.py` are now extracted individually.

### Testing

All 28 automated tests passed.

### Important observation

AST-aware chunking still produces oversized chunks. Large classes and methods may contain hundreds of lines.

More chunks do not automatically mean better retrieval. Retrieval quality must be evaluated separately.

## AST-aware chunking

- Learned how Python's Abstract Syntax Tree represents code.
- Used ast.parse() to inspect Python source code.
- Extracted classes, functions, methods, and nested functions.
- Preserved qualified names and source line numbers.
- Created class overview chunks separately from method implementations.
- Extracted module-level code while avoiding duplicated definitions.
- Handled decorators and one-line class definitions.
- Tested AST chunking with automated pytest tests.

## Requests repository inspection

- Python files loaded: 20
- AST chunks created: 349
- Average chunk size: approximately 17 lines
- Largest chunk: 145 lines