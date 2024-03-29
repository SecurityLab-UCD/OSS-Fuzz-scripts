import clang.cindex
from clang.cindex import TypeKind as CTypeKind, TokenKind as CTokenKind
import clang.enumerations
import inspect
import importlib.util
import ast
import astunparse
from typing import Any, List, Optional, Callable
import re

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


def py_get_func_code_demangled(file_path: str, name: str) -> Optional[str]:
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
    match name.split("."):
        case [function_name]:
            visitor = FunctionFinder(function_name)
        case [class_name, function_name]:
            visitor = InclassFunctionFinder(class_name, function_name)
        case _:
            visitor = FunctionFinder(name)

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


def py_get_class_code(file_path, class_name):
    with open(file_path, "r") as file:
        source_code = file.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Find the class definition node
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            class_node = node
            break

    if class_node is None:
        return None

    # Get the source code of the class
    start_line = class_node.lineno
    end_line = class_node.body[-1].lineno
    class_source_code = "\n".join(source_code.split("\n")[start_line - 1 : end_line])
    # Include the last function's body if it exists
    last_function_node = class_node.body[-1] if class_node.body else None
    if isinstance(last_function_node, ast.FunctionDef):
        end_line = last_function_node.body[-1].lineno
        class_source_code += "\n" + "\n".join(source_code.split("\n")[end_line - 1 :])
    return class_source_code


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


####################################################################################################
# *  "Purity" check for C/C++ functions
####################################################################################################


def c_get_params(code: str) -> Optional[list[tuple[CTypeKind, str]]]:
    """get parameters of a C function

    Args:
        code (str): source code of the function

    Returns:
        Optional[list[tuple[CTypeKind, str]]]:
            list of (type, name) parameter pairs, None if `code` is not a function
    """

    def walk_tree_for_params(node):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:  # type: ignore
            parameters = [
                (param.type.kind, param.spelling) for param in node.get_arguments()
            ]
            return parameters

        for child in node.get_children():
            result = walk_tree_for_params(child)
            if result is not None:
                return result

        return None

    index = clang.cindex.Index.create()
    unsaved_files = [("source.c", code)]
    tu = index.parse("source.c", unsaved_files=unsaved_files)

    return walk_tree_for_params(tu.cursor)


def is_c_primitive_type(type_kind: CTypeKind) -> bool:
    """Checks if a type is a C primitive type

    Args:
        type_kind (CTypeKind): a clang TypeKind object

    Returns:
        bool: True if the type is a C primitive type, False otherwise
    """
    # these function covers
    # TypeKind.BOOL,
    # TypeKind.CHAR_U,
    # TypeKind.UCHAR,
    # TypeKind.CHAR16,
    # TypeKind.CHAR32,
    # TypeKind.USHORT,
    # TypeKind.UINT,
    # TypeKind.ULONG,
    # TypeKind.ULONGLONG,
    # TypeKind.CHAR_S,
    # TypeKind.SCHAR,
    # TypeKind.WCHAR,
    # TypeKind.SHORT,
    # TypeKind.INT,
    # TypeKind.LONG,
    # TypeKind.LONGLONG,
    # TypeKind.FLOAT,
    # TypeKind.DOUBLE,
    # TypeKind.LONGDOUBLE,
    return CTypeKind.BOOL.value <= type_kind.value <= CTypeKind.LONGDOUBLE.value  # type: ignore


def c_use_global_variable(code: str) -> bool:
    """Checks if a C function uses global variables

    Args:
        code (str): source code of the function

    Returns:
        bool: True if the function uses global variables, False otherwise
    """
    index = clang.cindex.Index.create()
    unsaved_files = [("source.c", code)]
    tu = index.parse("source.c", unsaved_files=unsaved_files)

    # decision logic:
    # if a identifier is not a parameter and not declared in the function, it is a global variable
    parameters = [param.spelling for param in tu.cursor.get_arguments()]
    declared_variables = []

    prev_token = None
    for token in tu.cursor.get_tokens():
        # check for new variable declaration
        if token.kind == CTokenKind.IDENTIFIER:  # type: ignore
            var_name = token.spelling
            if (
                prev_token
                and prev_token.kind == CTokenKind.KEYWORD  # type: ignore
                and prev_token.spelling != "return"
            ):
                declared_variables.append(var_name)
            elif var_name not in parameters and var_name not in declared_variables:
                return True
        prev_token = token
    return False


def py_get_params(source_code: str) -> list[str]:
    tree = ast.parse(source_code)

    # Find all the function definitions in the AST
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    # Extract the parameter names from each function definition
    parameter_names = []
    for function in functions:
        for arg in function.args.args:
            parameter_names.append(arg.arg)

    return parameter_names


def py_use_global_variable(code: str) -> bool | None:
    """Checks if a Python function uses global variables

    Args:
        code (str): source code of the function
        func_name (str): name of the function

    Returns:
        bool: True if the function uses global variables, False otherwise
    """
    # backup plan if exec() + locals() fails
    params = set(py_get_params(code))
    assignments = set()
    names = set()
    lines = code.split("\n")

    def is_imported_module(node_name: str, lineno: int) -> bool:
        """if it is in form of node_name.xxx, we consider it as imported module"""
        line = lines[lineno - 1]
        idx = line.find(node_name) + len(node_name)
        return idx < len(line) and line[idx] == "."

    tree = ast.parse(code)

    for func in tree.body:
        if isinstance(func, ast.FunctionDef):
            # for node in func.body:
            for node in ast.walk(func):
                if isinstance(node, ast.Assign):
                    if isinstance(node.targets[0], ast.Tuple):
                        # multiple assignements, e.g. a, b = 1, 2
                        for target in node.targets[0].elts:
                            assignments.add(target.id)  # type: ignore
                    else:
                        # todo: more extensive type matching here
                        try:
                            assignments.add(node.targets[0].id)  # type: ignore
                        except:
                            pass
                elif isinstance(node, ast.Name):
                    if not is_imported_module(node.id, node.lineno):
                        names.add(node.id)

    likely_globals = names - assignments - params
    return bool(likely_globals)


def is_py_primitive_type(value: str) -> bool:
    """check if a value is a primitive type in Python.
    We consider only a object <class_name object at 0xsome_address> as non-primitive type

    Args:
        value (str): a reported value string

    Returns:
        bool: True if the value is a primitive type, False otherwise
    """
    pattern = r"<([^}]*) object at 0x([0-9a-fA-F]{12})>"
    match = re.match(pattern, value)
    return not bool(match)
