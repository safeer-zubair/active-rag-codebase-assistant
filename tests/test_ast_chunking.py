import ast

from src.ast_chunking import extract_source_segment

def test_extract_function_source():
    source_code = (
        "def greet(name):\n"
        "   return f'Hello, {name}'\n"
    )

    tree = ast.parse(source_code)

    function_node = tree.body[0]

    result = extract_source_segment(
        source_code,
        function_node
    )

    assert result == source_code.strip()


from src.ast_chunking import find_code_definitions


def test_find_classes_and_functions():
    source_code = """
class User:
    def greet(self):
        return "Hello"

def calculate_total(a, b):
    return a + b
"""

    definitions = find_code_definitions(source_code)

    names = [
        item["symbol_name"]
        for item in definitions
    ]

    assert names == [
        "User",
        "greet",
        "calculate_total",
    ]


def test_identify_methods_and_parent_classes():
    source_code = """
class Session:
    def request(self):
        pass

    def get(self):
        pass
"""

    definitions = find_code_definitions(source_code)

    methods = [
        item for item in definitions
        if item["symbol_type"] == "method"
    ]

    assert len(methods) == 2

    assert methods[0]["symbol_name"] == "request"
    assert methods[0]["parent_symbol"] == "Session"

    assert methods[1]["symbol_name"] == "get"
    assert methods[1]["parent_symbol"] == "Session"


def test_find_async_functions():
    source_code = """
async def fetch_data():
    return "data"
"""

    definitions = find_code_definitions(source_code)

    assert len(definitions) == 1
    assert definitions[0]["symbol_name"] == "fetch_data"
    assert definitions[0]["symbol_type"] == "function"

from src.ast_chunking import find_code_definitions


def test_find_classes_and_functions():
    source_code = """
class User:
    def greet(self):
        return "Hello"

def calculate_total(a, b):
    return a + b
"""

    definitions = find_code_definitions(source_code)

    names = [
        item["symbol_name"]
        for item in definitions
    ]

    assert names == [
        "User",
        "greet",
        "calculate_total",
    ]


def test_identify_methods_and_parent_classes():
    source_code = """
class Session:
    def request(self):
        pass

    def get(self):
        pass
"""

    definitions = find_code_definitions(source_code)

    methods = [
        item for item in definitions
        if item["symbol_type"] == "method"
    ]

    assert len(methods) == 2

    assert methods[0]["symbol_name"] == "request"
    assert methods[0]["parent_symbol"] == "Session"

    assert methods[1]["symbol_name"] == "get"
    assert methods[1]["parent_symbol"] == "Session"


def test_find_async_functions():
    source_code = """
async def fetch_data():
    return "data"
"""

    definitions = find_code_definitions(source_code)

    assert len(definitions) == 1
    assert definitions[0]["symbol_name"] == "fetch_data"
    assert definitions[0]["symbol_type"] == "function"

from src.ast_chunking import create_ast_chunks


def test_create_ast_chunks():
    source_code = (
        "class User:\n"
        "    def greet(self):\n"
        "        return 'Hello'\n"
    )

    file_data = {
        "file_path": "src/user.py",
        "content": source_code,
    }

    chunks = create_ast_chunks(file_data)

    assert len(chunks) == 2

    class_chunk = chunks[0]
    method_chunk = chunks[1]

    assert class_chunk["symbol_name"] == "User"
    assert class_chunk["symbol_type"] == "class"

    assert method_chunk["symbol_name"] == "greet"
    assert method_chunk["symbol_type"] == "method"
    assert method_chunk["parent_symbol"] == "User"

    assert method_chunk["start_line"] == 2
    assert method_chunk["end_line"] == 3

    assert "return 'Hello'" in method_chunk["content"]

# Test for decorators
def test_decorator_is_included_in_chunk():
    source_code = (
        "class User:\n"
        "    @property\n"
        "    def name(self):\n"
        "        return 'Safeer'\n"
    )

    file_data = {
        "file_path": "user.py",
        "content": source_code,
    }

    chunks = create_ast_chunks(file_data)

    method_chunk = next(
        chunk for chunk in chunks
        if chunk["symbol_name"] == "name"
    )

    assert method_chunk["start_line"] == 2
    assert "@property" in method_chunk["content"]

# test for nested functions
def test_nested_function_discovery():
    source_code = (
        "def outer():\n"
        "    def inner():\n"
        "        return True\n"
        "    return inner()\n"
    )

    definitions = find_code_definitions(source_code)

    assert len(definitions) == 2

    inner = next(
        item for item in definitions
        if item["symbol_name"] == "inner"
    )

    assert inner["qualified_name"] == "outer.inner"
    assert inner["parent_symbol"] == "outer"

# test nested methods
def test_nested_function_inside_method():
    source_code = (
        "class Session:\n"
        "    def request(self):\n"
        "        def validate():\n"
        "            return True\n"
        "        return validate()\n"
    )

    definitions = find_code_definitions(source_code)

    validate = next(
        item for item in definitions
        if item["symbol_name"] == "validate"
    )

    assert validate["symbol_type"] == "nested_function"
    assert validate["qualified_name"] == "Session.request.validate"

def test_extract_module_level_code():
    source_code = (
        "import requests\n"
        "import json\n"
        "\n"
        "DEFAULT_TIMEOUT = 30\n"
        "API_BASE_URL = 'https://example.com'\n"
        "\n"
        "class APIClient:\n"
        "    pass\n"
    )

    chunks = create_ast_chunks({
        "file_path": "api.py",
        "content": source_code,
    })

    module_chunks = [
        chunk for chunk in chunks
        if chunk["symbol_type"] == "module"
    ]

    assert len(module_chunks) == 1

    module_content = module_chunks[0]["content"]

    assert "import requests" in module_content
    assert "import json" in module_content
    assert "DEFAULT_TIMEOUT = 30" in module_content
    assert "API_BASE_URL" in module_content

    assert "class APIClient" not in module_content

def test_no_module_chunk_when_file_only_contains_definitions():
    source_code = (
        "def greet():\n"
        "    return 'Hello'\n"
    )

    chunks = create_ast_chunks({
        "file_path": "greetings.py",
        "content": source_code,
    })

    module_chunks = [
        chunk for chunk in chunks
        if chunk["symbol_type"] == "module"
    ]

    assert module_chunks == []

def test_module_code_after_class():
    source_code = (
        "class User:\n"
        "    pass\n"
        "\n"
        "DEFAULT_ROLE = 'guest'\n"
    )

    chunks = create_ast_chunks({
        "file_path": "user.py",
        "content": source_code,
    })

    module_chunks = [
        chunk for chunk in chunks
        if chunk["symbol_type"] == "module"
    ]

    assert len(module_chunks) == 1
    assert "DEFAULT_ROLE" in module_chunks[0]["content"]
    assert module_chunks[0]["start_line"] == 4

def test_finds_classes_inside_control_flow():
    source_code = """
if TYPE_CHECKING:
    class Example:
        pass
"""

    definitions = find_code_definitions(source_code)

    example = next(
        item for item in definitions
        if item["symbol_name"] == "Example"
    )

    assert example["symbol_type"] == "class"
    assert example["qualified_name"] == "Example"
    assert example["control_context"] == ["if TYPE_CHECKING"]


def test_finds_nested_function_inside_method():
    source_code = """
class User:
    def authenticate(self):
        if self.is_admin:
            def grant_access():
                return True
"""

    definitions = find_code_definitions(source_code)

    grant_access = next(
        item for item in definitions
        if item["symbol_name"] == "grant_access"
    )

    assert grant_access["symbol_type"] == "nested_function"
    assert (
        grant_access["qualified_name"]
        == "User.authenticate.grant_access"
    )
    assert grant_access["parent_symbol"] == "User.authenticate"


def test_preserves_method_classification():
    source_code = """
class User:
    def authenticate(self):
        return True
"""

    definitions = find_code_definitions(source_code)

    method = next(
        item for item in definitions
        if item["symbol_name"] == "authenticate"
    )

    assert method["symbol_type"] == "method"
    assert method["qualified_name"] == "User.authenticate"


def test_finds_definitions_inside_try_statement():
    source_code = """
try:
    class OptionalFeature:
        pass
except ImportError:
    def fallback():
        return None
"""

    definitions = find_code_definitions(source_code)

    names = {
        item["symbol_name"]
        for item in definitions
    }

    assert "OptionalFeature" in names
    assert "fallback" in names