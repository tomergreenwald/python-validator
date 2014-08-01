import ast

from validator.visitors.Visitors import ProgramVisitor

classes = {}
functions = {}
varz = {}

code = """

class A(object):
    def __init__(self, param):
        self.x = 5
        a = 'a'
        b = param

class B(A):
    def __init__(self):
        super(B, self).__init__()
        A.__init__(self)
a = A()
"""
ast_tree = ast.parse(code)
visitor = ProgramVisitor()
visitor.visit(ast_tree)