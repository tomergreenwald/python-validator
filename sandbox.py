import ast

from util import ClassRepresentation
from validator.visitors.ProgramVisitor import ProgramVisitor


code = """

def cc():
    return "cc"

class A(object):
    def __init__(self):
        self.x = 5
        self.c = cc()
        
class B(A):
    def __init__(self):
        super(B, self).__init__()
        A.__init__(self)
"""

ast_tree = ast.parse(code)
#FIXME: this initialization seems wrong but if we remove it exceptions are thrown because it is required
class_dictionary = {'object': ClassRepresentation('object'), 'Exception': ClassRepresentation('Exception')}
program_visitor = ProgramVisitor(class_dictionary)
program_visitor.visit(ast_tree)

for c in class_dictionary.values():
    c.methods = list(set(c.methods))

for c in class_dictionary.values():
    print c
