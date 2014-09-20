class Example(object):
    def __init__(self, code, description):
        self.code = code
        self.desc = description


examples = []

code1 = """
class A(object):
    pass

a = A()
a.x
"""
examples.append(
    Example(code1, 'Basic exmple, should create object of type A and state that the object does not have attribute x')
)
#Fails because the abstract state mishandles attributes
code1_5 = """
class A(object):
    def __init__(self, b):
        self.a = 1
        self.b = b

ttt = A("hello")
x = ttt.a
y = ttt.c
"""
examples.append(
    Example(code1_5,
            'Should create object of type A with two attributes - a and b. '
            'The first assignment should work since attribute a exists, '
            'The second assignment should state that ttt does not have attribute c'
    )
)
#Fails because __add__ was not defined anywhere
code2 = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

a = A()
a.x + a.y
a.x + a.z
"""
examples.append(
    Example(code2,
            'Should create object of type A with two attributes - x and y. '
            'The first add should work since both attribute x and y exists, '
            'The second add should state that a does not have attribute z'
    )
)
#fails for the same reason as 2
code3 = """
class A(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

a = A('Hello', 1)
a.x.isalpha()
a.y.isalpha()
"""
examples.append(
    Example(code3,
            'Created object of type A having two attributes, x is string and y is int.'
            'a.x.isalpha() should work since string has method isalpha,'
            'a.y.isalpha() should state that a.y does not have attribute isalpha()'
    )
)
#Fails because the abstract state doesn't recognize the registration of root#a at init_object
#you can see that there is an ereor print where there shouldn't be one
code4 = """
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
examples.append(
    Example(code4,
            'Created object of type A, a.foo_x() should work fine, '
            'a.foo_z() should state that a does not have attribute z, '
            'and a.foo_y() should state that a does not have attribute foo_y'
    )
)
#fails for the same reason as 4
code5 = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

    def foo_x(self):
        self.x = self.x + self.y

    def foo_xx(self):
        self.foo_x()

a = A()
a.foo_x()
a.foo_xx()
"""
examples.append(
    Example(code5,
            'Demonstrates that the method know each other'
    )
)
#fails for the same reason as 4
code6 = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

    def foo_z(self):
        self.z = 3

a = A()
a.m = 2
a.m
a.foo_z()
a.z
"""
examples.append(
    Example(code6,
            'Demonstrates adding attributes on the fly')
)
#fails for the same reason as 4 and 2
code7 = """
class A(object):
    def __init__(self):
        self.x = 1

class B(object):
    def __init__(self):
        self.y = 1

a = A()
b = B()
a.x + b.y
a.x + b.x
"""
examples.append(
    Example(code7,
            'Demonstrates using two different classes. a.x + b.y should be fine, the last call should state that b.x does not exists')
)
#fails for the same reason as 1
code8 = """
class A(object):
    def __init__(self):
        self.x = 1

class B(A):
    def __init__(self):
        self.y = 2

b = B()
b.y
b.x
"""
examples.append(
    Example(code8,
            'Demonstrate class inheritance - although B extends A, since B did not call to super ctor, b.x should not exists')
)
#fails because we mis-handle the super call
code9 = """
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
examples.append(
    Example(code9,
            'In this example, b.x+b.y should work, since we called the super ctor')
)
#fails because the abstract state doesn't lub well
code10 = """
class A(object):
    def __init__(self):
        self.x = 1

for x in [A(), A(), A()]:
    x.x

for x in [A(), A(), A()]:
    x.y
"""
examples.append(
    Example(code10,
            'List example')
)
#fails for the same reason as 10
code11 = """
class A(object):
    def __init__(self):
        self.x = 1

class B(object):
    def __init__(self):
        self.y = 1

for x in [A(), B()]:
    x.z
"""
examples.append(
    Example(code11,
            'List example2')
)
#fails because we mis-treat attribute assignment
code12 = """
class A(object):
    def __init__(self):
        self.x = 1

class B(object):
    def __init__(self):
        self.y = 1

a = A()
b = B()
b.y = a
b.b.x
a.x = 'a'
b.b.x
"""
examples.append(
    Example(code12,
            'Complex attribute example. Note the "pointers"')
)

import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import simpler

greetings = """
Welcome to the python attribute validator examples!
Any example starts with short description, continues with the code that will be checked, and the code after the simpler methods.
Next, the code will run through the validatior.

Note that we only demonstrate some core features. Full description of the validator capacity is in the doc.

There are 12 examples. Have fun! :)
"""
print greetings
raw_input('Press enter to start')
print

for example in examples:
    print example.desc
    print 'Orignal Code:'
    print example.code
    print
    simple = simpler.make_simple(example.code)
    print 'After simpler:'
    print '=============='
    print simple
    print

    ast_tree = ast.parse(simple)
    visitor = ProgramVisitor()
    visitor.visit(ast_tree)

    raw_input('Press enter to the next example')
    print

print 'Thank you'