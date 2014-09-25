import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import  simpler


code = """
class A(object):
    def __init__(self, b):
        self.a = 1
        self.b = b

a = A("hello")
a.a
a.c
"""

simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
