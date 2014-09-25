__author__ = 'Oded'
import sys
import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import simpler

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Code path for validate is missing.'
        exit(1)
    with file(sys.argv[1]) as f:
        code = f.read()

    print 'Orignal Code:'
    print code
    print
    simple = simpler.make_simple(code)
    print 'After simpler:'
    print '=============='
    print simple
    print

    ast_tree = ast.parse(simple)
    visitor = ProgramVisitor()
    visitor.visit(ast_tree)