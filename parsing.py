import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import  simpler

classes = {}
functions = {}
varz = {}

code = """
class A(object):
    def __init__(self):
        self.x = 1

class B(A):
    def __init__(self):
        A(self)
        self.y = 2

b = B()
#b.x + b.y
"""
simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
