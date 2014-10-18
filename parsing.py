import ast
from tabulate import tabulate
from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import  simpler


code = """
class A(object):
    def __init__(self, x):
        self.a = x

    def get_a(self):
        self.a.b = 2
        return self.a

a = A(2)
b = A(a)

aa = b.get_a()
aa.a
aa.b
"""


simple = simpler.make_simple(code)
print simple
ast_tree = ast.parse(simple)
visitor = ProgramVisitor()
visitor.visit(ast_tree)
headers = ["State #", "Action", "From", "To", "Errors"]
print tabulate(visitor.table, headers,tablefmt="grid")
for i in xrange(len(visitor.table)):
    visitor.table.pop()