import ast

from validator.visitors.Visitors import ProgramVisitor

classes = {}
functions = {}
varz = {}

code = """
#I would like True/False/None to be regular variables. So someone should register them to the abstract state before the
#ProgramVisitor runs
#a = True
#b = None
v = 5
v2 = 'a'
#v2.v = v
v3 = ''
v3.a = 5
v3.b = 'b'
#v3.v = v
#v2 = v3
"""
ast_tree = ast.parse(code)
visitor = ProgramVisitor()
visitor.visit(ast_tree)