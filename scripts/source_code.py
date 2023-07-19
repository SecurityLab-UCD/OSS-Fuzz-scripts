from _ast import AST
import clang.cindex
import inspect
import importlib.util
import ast
import astunparse
from typing import Any, Optional, Callable

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


# Visit AST to get in-class function
class InclassFunctionFinder(ast.NodeVisitor):
    def __init__(self, class_name: str = None, function_name: str = None):
        self.class_name = class_name
        self.function_name = function_name
        self.functions = {}

    def visit_ClassDef(self, node: AST):
        # Check class name
        if node.name == self.class_name:
            for body_node in node.body:
                if (
                    isinstance(body_node, ast.FunctionDef)
                    and body_node.name == self.function_name
                ):
                    self.functions[node.name] = astunparse.unparse(body_node)
                    break
        # Ensure traversal continues to the children of nodes that don't match the current mode.
        self.generic_visit(node)


# Visit AST to get function
class FunctionFinder(ast.NodeVisitor):
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.functions = {}

    def visit_FunctionDef(self, node: AST):
        # If this is the function we're looking for then save it
        if node.name == self.function_name or node.name in self.functions:
            self.functions[node.name] = astunparse.unparse(node)


# Extract Python project function code
def inspect_get_func_code_demangled(
    file_path: str, function_name: str, class_name: str = None
):
    # get all source code
    source_code = ""
    with open(file_path, "r") as source:
        source_code = source_code.join(source.read())

    # traverse AST tree to find target function code
    tree = ast.parse(source_code)

    # Check the function is defined in class or not
    if class_name == None:
        visitor = FunctionFinder(function_name)
        visitor.visit(tree)
    else:
        visitor = InclassFunctionFinder(class_name, function_name)
        visitor.visit(tree)
    # get the result
    function_source_code = ""
    for function_name, function_code in visitor.functions.items():
        if function_code is not None:
            function_source_code = function_source_code.join(function_code)

    return function_source_code


# todo: Java

CODE_EXTRACTOR = {
    "c": clang_get_func_code,
    "cpp": clang_get_func_code_demangled,
    "python": inspect_get_func_code_demangled,
}
