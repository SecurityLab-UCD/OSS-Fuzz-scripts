from source_code import *

a = inspect_get_func_code_demangled(
    "/home/hxxzhang/python-io-capture/example_project/person.py", "introduce"
)
print(a)

# import ast
# import astunparse


# class MethodFinder(ast.NodeVisitor):
#     def __init__(self, class_name, method_name):
#         self.class_name = class_name
#         self.method_name = method_name

#     def visit_ClassDef(self, node):
#         print(node.name)
#         if node.name == self.class_name:
#             for body_node in node.body:
#                 if (
#                     isinstance(body_node, ast.FunctionDef)
#                     and body_node.name == self.method_name
#                 ):
#                     print(astunparse.unparse(body_node))
#                     break
#         self.generic_visit(node)


# source_code = """
# import util


# class Person:

#     def __init__(self, name, age):
#         self.name = name
#         self.age = age

#     def introduce(self):

#         return f"Hi, my name is {self.name} and I am {self.age} years old."

#     def __repr__(self):
#         return util.format_repr(
#             self.__class__.__qualname__, name=self.name, age=self.age
#         )


# class Student(Person):
#     def __init__(self, name, age, sid):
#         Person.__init__(self, name, age)
#         self.id = sid

#     def introduce(self):
#         return f"{super().introduce()} , and I am a student in UC Davis."

# """

# tree = ast.parse(source_code)
# finder = MethodFinder("Student", "introduce")
# finder.visit(tree)
