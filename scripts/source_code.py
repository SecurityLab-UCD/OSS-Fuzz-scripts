import clang.cindex
import inspect
import importlib.util
import ast
import astunparse
from typing import Optional, Callable

# from scripts.common import LLVM, LIBCLANG

# clang.cindex.Config.set_library_file(LIBCLANG)


def clang_get_func_code(
    file_path: str,
    function_name: str,
    get_node_name: Callable[[clang.cindex.Cursor], str] = lambda node: node.spelling,
) -> Optional[str]:
    """Extracts the source code of a function from a C/C++ file.

    Args:
        file_path (str): path to the source code file
        function_name (str): name of the function

    Returns:
        Optional[str]: source code of the function, None if not found
    """
    # Create an index for the translation unit
    index = clang.cindex.Index.create()

    # Parse the translation unit
    tu = index.parse(file_path)

    # Traverse the AST to find the function
    for node in tu.cursor.walk_preorder():
        if (
            node.kind
            in {
                clang.cindex.CursorKind.FUNCTION_DECL,  # type: ignore
                clang.cindex.CursorKind.CXX_METHOD,  # type: ignore
            }
            and get_node_name(node) == function_name
            and node.is_definition()
        ):
            # Get the source range of the function
            start_location = node.extent.start
            end_location = node.extent.end

            # Extract the source code of the function
            with open(file_path, "r") as f:
                lines = f.readlines()
                function_source_code = "".join(
                    lines[start_location.line - 1 : end_location.line]
                )

            return function_source_code

    return None


def clang_get_func_code_demangled(file_path: str, function_name: str):
    return clang_get_func_code(file_path, function_name, lambda node: node.displayname)


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, function_name):
        self.function_name = function_name
        self.functions = {}

    def visit_FunctionDef(self, node):
        # If this is the function we're looking for, or it's a function we've previously found
        # and saved because it was called in the function we're looking for, save its source code.
        if node.name == self.function_name or node.name in self.functions:
            self.functions[node.name] = astunparse.unparse(node)

        # If this function calls another function that we haven't found yet, save that function's name.
        # The next time we encounter a FunctionDef node with that name, we'll save its source code.
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                if call.func.id not in self.functions:
                    self.functions[call.func.id] = None


# todo: Java, Python
def inspect_get_func_code_demangled(file_path: str, function_name: str):
    source_code = ""
    with open(file_path, "r") as source:
        source_code = source_code.join(source.read())

    tree = ast.parse(source_code)

    visitor = FunctionVisitor(function_name)
    visitor.visit(tree)

    function_source_code = ""
    for function_name, function_code in visitor.functions.items():
        if function_code is not None:
            function_source_code = function_source_code.join(function_code)

    return function_source_code


# Only get single function source code, can not deal with function call
def inspect_get_func_code_demangled_2(file_path: str, function_name: str):
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    return inspect.getsource(function)


CODE_EXTRACTOR = {
    "c": clang_get_func_code,
    "cpp": clang_get_func_code_demangled,
    "python": inspect_get_func_code_demangled,
}
