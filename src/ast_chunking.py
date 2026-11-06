import ast

def extract_source_segment(
    source_code: str,
    node: ast.AST,
) -> str | None:
    """
    Extract the original source code belonging to an AST node,
    including decorators when present
    """

    lines = source_code.splitlines()

    start_line = get_definition_start_line(node)
    end_line = node.end_lineno

    if end_line is None:
        return None

    return "\n".join(
        lines[start_line - 1:end_line]
    )

def find_code_definitions(source_code: str) -> list[dict]:
    """
    Find classes and functions throughout a Python AST

    Supports definitions nested inside control-flow statements,
    classes and functions

    Each definition stores its qualified name, parent,
    source line range and enclosing control-flow context
    """

    tree = ast.parse(source_code)
    definitions = []

    control_node_types = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
        ast.Match,
    )

    def get_control_label(node: ast.AST) -> str:
        """Create a readable label for a control-flow node"""

        if isinstance(node, ast.If):
            return f"if {ast.unparse(node.test)}"

        if isinstance(node, ast.Match):
            return f"match {ast.unparse(node.subject)}"

        return type(node).__name__

    def visit_node(
        node: ast.AST,
        parent_symbol: str | None = None,
        scope_kind: str = "module",
        function_depth: int = 0,
        control_context: tuple = (),
    ):
        # Handle class definitions
        if isinstance(node, ast.ClassDef):
            symbol_name = node.name

            qualified_name = (
                f"{parent_symbol}.{symbol_name}"
                if parent_symbol
                else symbol_name
            )

            definitions.append({
                "symbol_name": symbol_name,
                "qualified_name": qualified_name,
                "symbol_type": "class",
                "parent_symbol": parent_symbol,
                "control_context": list(control_context),
                "start_line": get_definition_start_line(node),
                "end_line": node.end_lineno,
                "node": node,
            })

            # A class creates a new class scope
            # Its directly declared functions are methods
            for child in node.body:
                visit_node(
                    child,
                    parent_symbol=qualified_name,
                    scope_kind="class",
                    function_depth=0,
                    control_context=control_context,
                )

            return

        # Handle normal and asynchronous functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbol_name = node.name

            qualified_name = (
                f"{parent_symbol}.{symbol_name}"
                if parent_symbol
                else symbol_name
            )

            if scope_kind == "class" and function_depth == 0:
                symbol_type = "method"
            elif function_depth > 0:
                symbol_type = "nested_function"
            else:
                symbol_type = "function"

            definitions.append({
                "symbol_name": symbol_name,
                "qualified_name": qualified_name,
                "symbol_type": symbol_type,
                "parent_symbol": parent_symbol,
                "control_context": list(control_context),
                "start_line": get_definition_start_line(node),
                "end_line": node.end_lineno,
                "node": node,
            })

            # Definitions inside this function are nested
            for child in node.body:
                visit_node(
                    child,
                    parent_symbol=qualified_name,
                    scope_kind="function",
                    function_depth=function_depth + 1,
                    control_context=control_context,
                )

            return

        # Track control-flow context without treating it
        # as a new class or function scope
        if isinstance(node, control_node_types):
            label = get_control_label(node)
            control_context = control_context + (label,)

        # Recursively inspect all child nodes
        for child in ast.iter_child_nodes(node):
            visit_node(
                child,
                parent_symbol=parent_symbol,
                scope_kind=scope_kind,
                function_depth=function_depth,
                control_context=control_context,
            )

    visit_node(tree)

    return sorted(
        definitions,
        key=lambda item: (
            item["start_line"],
            item["end_line"],
        ),
    )

def extract_class_overview(
    source_code: str,
    node: ast.ClassDef,
) -> str:
    """
    Extract a class declaration, decorators,
    inheritance and docstring without method bodies
    """

    lines = source_code.splitlines()
    start_line = get_definition_start_line(node)

    # Handle one-line class definitions
    if node.body[0].lineno == node.lineno:
        return "\n".join(
            lines[start_line - 1:node.end_lineno]
        )

    class_header_end = node.body[0].lineno - 1
    docstring = ast.get_docstring(node)

    if docstring:
        first_statement = node.body[0]

        if (
            isinstance(first_statement, ast.Expr)
            and isinstance(first_statement.value, ast.Constant)
            and isinstance(first_statement.value.value, str)
        ):
            class_header_end = first_statement.end_lineno

    return "\n".join(
        lines[start_line - 1:class_header_end]
    )

def create_ast_chunks(file_data: dict) -> list[dict]:
    """
    Create AST-aware chunks from a Python file
    """

    source_code = file_data["content"]
    file_path = file_data["file_path"]

    definitions = find_code_definitions(source_code)

    chunks = create_module_chunks(
        source_code,
        file_path,
    )

    for definition in definitions:
        node = definition["node"]

        if definition["symbol_type"] == "class":
            content = extract_class_overview(
                source_code,
                node,
            )
        else:
            content = extract_source_segment(
                source_code,
                node,
            )

        if content is None or not content.strip():
            continue

        start_line = definition["start_line"]

        if definition["symbol_type"] == "class":
            overview_lines = content.splitlines()
            end_line = start_line + len(overview_lines) - 1
        else:
            end_line = definition["end_line"]

        chunk = {
            "chunk_id": (
                f"{file_path}:{definition['qualified_name']}:"
                f"{start_line}-{end_line}"
            ),
            "file_path": file_path,
            "symbol_name": definition["symbol_name"],
            "qualified_name": definition["qualified_name"],
            "symbol_type": definition["symbol_type"],
            "parent_symbol": definition["parent_symbol"],
            "control_context": definition["control_context"],
            "start_line": start_line,
            "end_line": end_line,
            "content": content,
        }

        chunks.append(chunk)

    return chunks

def get_definition_start_line(node: ast.AST) -> int:
    """
    Get the starting line of a definition,
    including its decorators
    """

    start_line = node.lineno

    if hasattr(node, "decorator_list") and node.decorator_list:
        decorator_lines = [
            decorator.lineno
            for decorator in node.decorator_list
        ]

        start_line = min(
            start_line,
            *decorator_lines,
        )

    return start_line

def contains_code_definition(node: ast.AST) -> bool:
    """
    Check whether a statement contains a class
    or function definition
    """

    definition_types = (
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )

    for child in ast.walk(node):
        if isinstance(child, definition_types):
            return True

    return False

def create_module_chunks(
    source_code: str,
    file_path: str,
) -> list[dict]:
    """
    Extract module-level code without duplicating
    separately extracted class and function definitions
    """

    tree = ast.parse(source_code)
    lines = source_code.splitlines()

    definition_types = (
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )

    chunks = []

    def get_clean_source(nodes) -> tuple[int, int, str]:
        """
        Extract module source while blanking separately
        extracted class and function definitions

        Preserve original line positions
        """

        start_line = nodes[0].lineno
        end_line = nodes[-1].end_lineno

        content_lines = lines[start_line - 1:end_line].copy()

        for root_node in nodes:
            for child in ast.walk(root_node):

                if isinstance(child, definition_types):
                    definition_start = get_definition_start_line(child)
                    definition_end = child.end_lineno

                    for line_number in range(
                        definition_start,
                        definition_end + 1,
                    ):
                        index = line_number - start_line

                        if 0 <= index < len(content_lines):
                            content_lines[index] = ""

        return (
            start_line,
            end_line,
            "\n".join(content_lines),
        )

    def save_group(nodes):
        if not nodes:
            return

        start_line, end_line, content = get_clean_source(nodes)

        if not content.strip():
            return

        chunks.append({
            "chunk_id": f"{file_path}:module:{start_line}-{end_line}",
            "file_path": file_path,
            "symbol_name": "__module__",
            "symbol_type": "module",
            "parent_symbol": None,
            "start_line": start_line,
            "end_line": end_line,
            "content": content,
        })

    current_group = []

    for node in tree.body:

        if isinstance(node, definition_types):
            save_group(current_group)
            current_group = []
            continue

        current_group.append(node)

    save_group(current_group)

    return chunks