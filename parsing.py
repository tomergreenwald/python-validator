import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import  simpler


code = """
class A(object):
    def __init__(self, a):
        self.a = a

class B(object):
    def __init__(self, b):
        self.b = b

a = A(1)
b = B(a)

# First group
a.a
b.b
b.b.a

# Second group
b.b.b
a.b

# Third group
a.c = 2
b.b.c
"""

simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
