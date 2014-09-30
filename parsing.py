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

code_simple_functions = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

    def foo_x(self):
        self.x = self.x + self.y
        self.z = self.x + self.y
        self.w = self.z + self.y + self.x

    def foo_z(self):
        # self.x = self.x + self.y + self.z
        self.need_int = self.w
        self.need_top = self.y * self.x

a = A()
a.foo_x()
a.foo_z()
# a.foo_y()
"""

code = """
class A(object):
    def __init__(self):
        self.a = 1

for x in [A(), A(), A()]:
    x.a

# for x in [A(), A(), A()]:
#     x.b
"""

simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
