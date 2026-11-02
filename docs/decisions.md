# Technical Decisions

## Decision 001: Python Virtual Environment

### Decision
Use a project-specific Python virtual environment.

### Reason
To isolate project dependencies and avoid conflicts
with other Python projects.

### Alternatives
- Global Python package installation.
- Conda environment.

### Outcome
Using Python venv.

## Fixed-Size Chunking Configuration

### Decision

The initial chunking strategy uses line-based fixed-size chunks.

### Configuration

- Chunk size: 40 lines
- Overlap: 8 lines
- Step size: 32 lines

### Rationale

Line-based chunking was selected because Python source code is
organized into lines and our system needs to preserve accurate
source-code line references.

An overlap of 8 lines provides shared context between adjacent
chunks and reduces the chance of losing context at chunk boundaries.

These values are initial experimental settings, not proven
optimal parameters.

### Limitations

Fixed-size chunking does not understand Python syntax or code
structure. Functions and classes may be split across chunks.

This limitation motivates the later AST-aware chunking experiment.

## Decision: recursively traverse the AST

**Decision:** Recursively traverse AST child nodes to discover definitions inside control-flow structures.

**Reason:** Restricting discovery to direct module, class, and function bodies misses valid Python definitions inside structures such as `if TYPE_CHECKING`.

**Metadata:** Store enclosing control-flow context separately from the qualified name.

**Validation:** Six previously missed classes in Requests' `_types.py` were successfully extracted. The test suite passed all 28 tests.

**Trade-off:** Recursive discovery improves definition coverage, but AST-aware chunks can still be very large. Oversized-chunk handling remains a separate improvement.