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
        super(B, self).__init__()
        self.y = 2

b = B()
b.x + b.y
"""

code = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

    def foo_x(self):
        self.x = self.x + self.y

    def foo_z(self):
        self.x = self.x + self.y + self.z

a = A()
a.foo_x()
a.foo_z()
a.foo_y()
"""

simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
