import ast

from validator.visitors.Visitors import ProgramVisitor

classes = {}
functions = {}
varz = {}

code = """
#I would like True/False/None to be regular variables. So someone should register them to the abstract state before the
#ProgramVisitor runs
a = True
b = False
c = None
v = 5
v2 = 'a'
v2.v = v
v3 = ''
v3.a = 5
v3.b = 'b'
v3.v = v
v2 = v3.v
a_list = (a,b,c, 's')
a_tuple = [a,b,c, 's']
a_dict = {1:1}

if True:
    e = 5
    p = 8
elif 5==5:
    e = 6
else:
    e = 7

if 1==2:
    aa = 1

def func2(arg11):
    ii = arg11

def func1(arg1, arg2, def1 = 1, def2 = None):
    i = 1
    bfunc = arg1
    local = v3.a
    z = func2(arg1)
#1==1
#func1(a)
a1 = func1(2, 1, def2 = 'stringy')
#check = bfunc
"""
ast_tree = ast.parse(code)
visitor = ProgramVisitor()
visitor.visit(ast_tree)