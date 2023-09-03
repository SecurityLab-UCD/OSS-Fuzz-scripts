import clang.cindex
import inspect
import importlib.util
import ast
import astunparse
from typing import Any, List, Optional, Callable

from scripts.common import LLVM, LIBCLANG

clang.cindex.Config.set_library_file(LIBCLANG)


def clang_get_func_code(
    file_path: str,
    function_name: str,
    correct_node: Callable[
        [clang.cindex.Cursor, str], bool
    ] = lambda node, name: node.spelling
    == name,
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
            and correct_node(node, function_name)
            and node.is_definition()
        ):
            # Get the source range of the function
            start_location = node.extent.start
            end_location = node.extent.end

            # Extract the source code of the function
            with open(file_path, "r", errors="ignore") as f:
                lines = f.readlines()
                function_source_code = "".join(
                    lines[start_location.line - 1 : end_location.line]
                )

            return function_source_code

    return None


def clang_get_func_code_mangled(file_path: str, mangled_name: str):
    return clang_get_func_code(
        file_path,
        mangled_name,
        lambda node, mangled_name: node.mangled_name == mangled_name,
    )


class InclassFunctionFinder(ast.NodeVisitor):
    """
    Visit AST to get in-class function from a Python file
    """

    def __init__(self, class_name: str | None = None, function_name: str | None = None):
        self.class_name = class_name
        self.function_name = function_name
        self.functions = {}

    def visit_ClassDef(self, node: ast.AST):
        # Check class name
        if node.name == self.class_name:  # type: ignore
            for body_node in node.body:  # type: ignore
                if (
                    isinstance(body_node, ast.FunctionDef)
                    and body_node.name == self.function_name
                ):
                    self.functions[node.name] = astunparse.unparse(body_node)  # type: ignore
                    break
        # Ensure traversal continues to the children of nodes that don't match the current mode.
        self.generic_visit(node)


class FunctionFinder(ast.NodeVisitor):
    """
    Visit AST to get function from a Python file
    """

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.functions = {}

    def visit_FunctionDef(self, node: ast.AST):
        # If this is the function we're looking for then save it
        if node.name == self.function_name or node.name in self.functions:  # type: ignore
            self.functions[node.name] = astunparse.unparse(node)  # type: ignore


def py_get_func_code_demangled(
    file_path: str, function_name: str, class_name: str | None = None
) -> Optional[str]:
    """Extracts the source code of a function from a Python file.

    Args:
        file_path (str): path to the source code file
        function_name (str): name of the function
        class_name (str): name of the class

    Returns:
        Optional[str]: source code of the function, None if not found
    """
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

    function_source_code = "".join(
        function_code
        for function_code in visitor.functions.values()
        if function_code is not None
    )

    return function_source_code if function_source_code else None


# todo: Java

# Only C++ uses the file extensions (since we need to look at source file language for C++ projects),
# use the language as specified in the project's project.yaml otherwise
CODE_EXTRACTOR = {
    "c": clang_get_func_code,
    "cpp": clang_get_func_code_mangled,
    "cc": clang_get_func_code_mangled,
    "cxx": clang_get_func_code_mangled,
    "python": py_get_func_code_demangled,
}


def py_get_imported_modules(code: str) -> List[str]:
    """given python source code, return all imported modules' name

    Args:
        code (str): python source code

    Returns:
        List[str]: all imported modules's name in the source code
    """
    module_names = []
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_names.append(alias.asname if alias.asname else alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    module_names.append(alias.name)
            else:
                for alias in node.names:
                    module_names.append(alias.name.split(".")[0])
    return module_names
