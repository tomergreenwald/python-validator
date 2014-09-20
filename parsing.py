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
        self.y = 2

a = A()
a.x + a.y
a.x + a.z
"""

simple = simpler.make_simple(code)
#print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)