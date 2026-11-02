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

        content = extract_source_segment(
            source_code,
            node,
        )

        if content is None:
            continue

        start_line = definition["start_line"]
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

def create_module_chunks(
    source_code: str,
    file_path: str,
) -> list[dict]:
    """
    Extract consecutive module-level statements
    that are outside classes and functions
    """

    tree = ast.parse(source_code)
    lines = source_code.splitlines()

    module_nodes = [
        node
        for node in tree.body
        if not isinstance(
            node,
            (
                ast.ClassDef,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    if not module_nodes:
        return []

    chunks = []
    current_group = []

    def save_group(nodes):
        if not nodes:
            return

        start_line = nodes[0].lineno
        end_line = nodes[-1].end_lineno

        content = "\n".join(
            lines[start_line - 1:end_line]
        )

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

    for node in module_nodes:
        if current_group:
            previous_node = current_group[-1]

            has_definition_between = any(
                isinstance(
                    intervening_node,
                    (
                        ast.ClassDef,
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and previous_node.end_lineno < intervening_node.lineno
                and intervening_node.end_lineno < node.lineno
                for intervening_node in tree.body
            )

            if has_definition_between:
                save_group(current_group)
                current_group = []

        current_group.append(node)

    save_group(current_group)

    return chunks