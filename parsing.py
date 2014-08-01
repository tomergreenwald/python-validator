import ast

from validator.visitors.Visitors import ProgramVisitor

classes = {}
functions = {}
varz = {}

code = """
v = 5
v2 = 'a'
v2.v = v
v3 = ''
v3.a = 5
v3.b = 'b'
v3.v = v
v2 = v3
"""
ast_tree = ast.parse(code)
visitor = ProgramVisitor()
visitor.visit(ast_tree)