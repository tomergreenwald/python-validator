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
a.x
"""
examples.append(
    Example(code1, 'Basic example, should create object of type A and state that the object does not have attribute x.'
                   'After the first call, the validator adds the attribute x to the abstract state of a, '
                   'so it should state that the second call to a.x is legal.')
)
#Fails because the abstract state mishandles attributes
code14 = """
class A(object):
    def __init__(self, b):
        self.a = 1
        self.b = b

a = A("hello")
x = a.a
y = a.c
"""
examples.append(
    Example(code14,
            'Should create object of type A with two attributes - a and b. '
            'The first assignment should work since attribute a exists, '
            'The second assignment should state that a does not have attribute c'
    )
)

code15 = """
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
examples.append(code15,
                'Should create object a of type A and object b of type B that holds a.'
                'All the calls in the First group are valid, since that attributes are correct.'
                'In the second group, b.b.b does not exists, so it should raise error. After this statement, '
                'since in the abstract world we added attribute b to b.b, the call to a.b should be legal.'
                'In the third group, we add attribute c to a.c, so now it should state that b.b.c exists.'
)

code7 = """
class A(object):
    def __init__(self, a):
        self.a = a

class B(object):
    def __init__(self, b):
        self.b = b

class C(object):
    def __init__(self, c):
        self.c = c

a = A(1)
b = B(a)
c = C(a)

b.b.a
c.c.a

b.b.d = 3
c.c.d
"""
examples.append(code7,
                'Two objects - b (of type B) and a (of type A) which shared object (a of type A). '
                'After we add to a attribute d throw b.b.d, that attribute should exists in c.c.d as well.'
)

code14 = """
class A(object):
    def __init__(self):
        self.x = 1
        self.y = 2

a.x + a.y
"""
examples.append(
    Example(code14,
            'The validator should understand that a.x and a.y are ints, so the addition operator is valid.'
    )
)

#fails for the same reason as 2
code15 = """
class A(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

a = A('Hello', 1)
a.x.isalpha()
a.y.isalpha()
"""
examples.append(
    Example(code15,
            'Created object of type A having two attributes, x is string and y is int.'
            'The method isalpha() is a builtin method for strings only.'
            'Therefore the first call should be legal, and the second should state that the method does not exists.'
    )
)

# For some reason we get an error while registering foo_x because the abstract state doesn't recognize root#a
# but when we register foo_x it recognizes root#a, maybe because it is during the preciuos registration it created
# root#a
code7 = """
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
    Example(code7,
            'Created object of type A, a.foo_x() should work fine, '
            'a.foo_z() should state that a does not have attribute z, '
            'and a.foo_y() should state that a does not have method foo_y'
    )
)

code14 = """
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
    Example(code14,
            'Demonstrates the call from one method to another in the same object.'
    )
)

code15 = """
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
    Example(code15,
            'Demonstrates adding attributes on the fly')
)

#fails for the same reason as 7
code14 = """
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
    Example(code14,
            'Demonstrate class inheritance - although B extends A, since B did not call to super ctor, b.x should not exists')
)
#fails because we mis-handle the super call
code15 = """
class A(object):
    def __init__(self):
        self.x = 1

class B(A):
    def __init__(self):
        super(B, self).__init__()
        self.y = 2

b = B()
b.x
b.y
"""
examples.append(
    Example(code15,
            'In this example, b.x and b.y exists, since we called the super ctor')
)

#fails because the abstract state doesn't lub well
code14 = """
class A(object):
    def __init__(self):
        self.x = 1

for x in [A(), A(), A()]:
    x.x

for x in [A(), A(), A()]:
    x.y
"""
examples.append(
    Example(code14,
            'List example, we store the list as a LUB of all the elements,'
            'Easy to see that x.x should be fine and x.y does not exists.')
)

#fails for the same reason as 10
code15 = """
class A(object):
    def __init__(self, x):
        self.x = x

class B(object):
    def __init__(self, x):
        self.x = x
        self.y = 1

for x in [A(), B()]:
    x.x
    x.y
    x.z
"""
examples.append(
    Example(code15,
            'List example 2')
)

#fails because we mis-treat attribute assignment
code14 = """
class A(object):
    pass

a = A()
if True:
    a.a = 1
else:
    a.a = 1
    a.y = 2
a.a
a.y
"""
examples.append(
    Example(code14,
            'If-Else example, a.a should exists in any case, a.y exists just for the else')
)

code15 = """
class A(object):
    pass

a = A()
try:
    a.a = 2
    a.b = 3
except:
    a.a = 2

a.a
a.b
"""
examples.append(
    Example(code15,
            'try-except example.')
)

import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import simpler

greetings = """
Welcome to the python attribute validator examples!
Any example starts with short description, continues with the code that will be checked, and the code after the simpler methods.
Next, the code will run through the validatior.

Note that we only demonstrate some core features. Full description of the validator capacity is in the doc.

There are 15 examples. Have fun! :)
"""
print greetings
raw_input('Press enter to start')
print

for example in examples:
    print example.desc
    print 'Orignal Code:'
    print '============='
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