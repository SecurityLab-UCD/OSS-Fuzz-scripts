# from source_code import *
import ast
import astunparse

# Get the source code
# source_code = inspect_get_func_code_demangled(
#     "/home/hxxzhang/python-io-capture/example_project/example.py", "sum_v2"
# )
# print(source_code)

import ast
import astunparse


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


source_code = """
def foo():
    bar()
    baz()
    print('foo')

def bar():
    baz()
    print('bar')

def baz():
    print('baz')
"""

tree = ast.parse(source_code)
visitor = FunctionVisitor("foo")
visitor.visit(tree)

for function_name, function_code in visitor.functions.items():
    if function_code is not None:
        print(f"--- {function_name} ---")
        print(function_code)
