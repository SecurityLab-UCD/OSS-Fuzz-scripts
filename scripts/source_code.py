import clang.cindex
from typing import Optional
from scripts.common import LLVM, LIBCLANG

clang.cindex.Config.set_library_file(LIBCLANG)


def clang_get_func_code(file_path: str, function_name: str) -> Optional[str]:
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
            node.kind == clang.cindex.CursorKind.FUNCTION_DECL
            and node.spelling == function_name
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


# todo: Java, Python

CODE_EXTRACTOR = {
    "c": clang_get_func_code,
    "cpp": clang_get_func_code,
}