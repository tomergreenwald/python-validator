class Example(object):
    def __init__(self, code, description):
        self.code = code
        self.desc = description


examples = []

code1 = """
class A(object):
    pass

a = A()
a.a
a.a
"""
examples.append(
    Example(code1, 'Basic example, should create object of type A and state that the object does not have attribute a.'
                   'After the first call, the validator adds the attribute a to the abstract state of a, '
                   'so it should state that the second call to a.a is legal.')
)

#Fails because the abstract state mishandles attributes
code2 = """
class A(object):
    def __init__(self):
        self.a = 1

a = A()
a.a
a.c
"""
examples.append(
    Example(code2,
            'Should create object of type A with attribute a. '
            'The call to a.a should work fine since the attribute exists, '
            'The second assignment should state that a does not have attribute c'
    )
)

code3 = """
class A(object):
    def __init__(self, x):
        self.a = x

class B(object):
    def __init__(self, x):
        self.b = x

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
examples.append(
    Example(code3,
            'First thing you are going to see is the simpler work. It never leaves the arguments as is, '
            'and advance calls as b.b.a changes to two calls.'
            'In this example we create object a of type A and object b of type B that holds a.'
            'All the calls in the First group are valid, since that attributes are correct.'
            'In the second group, b.b.b does not exists, so it should raise error. After this statement, '
            'since in the abstract world we added attribute b to b.b, the call to a.b should be legal.'
            'In the third group, we add attribute c to a.c, so now it should state that b.b.c exists.'
    )
)

code4 = """
class A(object):
    def __init__(self, x):
        self.a = x

class B(object):
    def __init__(self, x):
        self.b = x

class C(object):
    def __init__(self, x):
        self.c = x

a = A(1)
b = B(a)
c = C(a)

b.b.a
c.c.a

b.b.d = 3
c.c.d
"""
examples.append(
    Example(code4,
            'Two objects - b (of type B) and a (of type A) which shared object (a of type A). '
            'After we add to a attribute d throw b.b.d, that attribute should exists in c.c.d as well.'
    )
)

code5 = """
class A(object):
    def __init__(self):
        self.a = 1
        self.b = 2

a = A()
a.a + a.b
"""
examples.append(
    Example(code5,
            'The validator should understand that a.a and a.b are ints, so the addition operator is valid.'
    )
)

#fails for the same reason as 2
code6 = """
class A(object):
    def __init__(self, x, y):
        self.a = x
        self.b = y

a = A('Hello', 1)
a.a.isalpha()
a.b.isalpha()
"""
examples.append(
    Example(code6,
            'Create object of type A having two attributes, a is string and b is int.'
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
        self.a = 1
        self.b = 2

    def foo_a(self):
        self.a += self.b

    def foo_c(self):
        self.a += self.b + self.c

a = A()
a.foo_a()
a.foo_c()
a.foo_b()
"""
examples.append(
    Example(code7,
            'Created object of type A, a.foo_a() should work fine, '
            'a.foo_c() should state that a does not have attribute c, '
            'and a.foo_b() should state that a does not have method foo_b'
    )
)

code8 = """
class A(object):
    def __init__(self):
        self.a = 1
        self.b = 2

    def foo_a(self):
        self.a += self.b

    def foo_aa(self):
        self.foo_a()

a = A()
a.foo_a()
a.foo_aa()
"""
examples.append(
    Example(code8,
            'Demonstrates the call from one method to another in the same object.'
    )
)

code9 = """
class A(object):
    def __init__(self):
        self.a = 1
        self.b = 2

    def foo_c(self):
        self.c = 3

a = A()
a.m = 2
a.m
a.foo_c()
a.c
"""
examples.append(
    Example(code9,
            'Demonstrates adding attributes on the fly')
)

#fails for the same reason as 7
code10 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(A):
    def __init__(self):
        self.b = 2

b = B()
b.b
b.a
"""
examples.append(
    Example(code10,
            'Demonstrate class inheritance - although B extends A, since B did not call to super ctor, '
            'b.a should not exists')
)

#fails because we mis-handle the super call
code11 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(A):
    def __init__(self):
        super(B, self).__init__()
        self.b = 2

b = B()
b.a
b.b
"""
examples.append(
    Example(code11,
            'In this example, b.a and b.b exists, since we called the super ctor')
)

#fails because the abstract state doesn't lub well
code12 = """
class A(object):
    def __init__(self):
        self.a = 1

for x in [A(), A(), A()]:
    x.a

for x in [A(), A(), A()]:
    x.b
"""
examples.append(
    Example(code12,
            'List example, we store the list as a LUB of all the elements,'
            'Easy to see that x.a should be fine and x.b does not exists.')
)

#fails for the same reason as 10
code13 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(object):
    def __init__(self, x):
        self.a = x
        self.b = 1

a = A()
b = B(a)
for x in [a, b]:
    x.a
    x.b
    x.c
"""
examples.append(
    Example(code13,
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
    a.b = 2
a.a
a.b
"""
examples.append(
    Example(code14,
            'If-Else example, a.a should exists in any case, a.b exists just for the else')
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
    a.c = 3

a.a
a.b
a.c
"""
examples.append(
    Example(code15,
            'try-except example.')
)

code16 = """
class A(object):
    pass

a = A()
try:
    a.a = 2
    a.b = 3
except:
    a.a = 2
    a.c = 3
finally:
    a.d = 2

a.a
a.b
a.c
a.d
"""
examples.append(
    Example(code16,
            'try-except-finally example.')
)

code17 = """
"""
examples.append(
    Example(code17,
            'methods lub example.')
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
raw_input('Hit any key to start')
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

    raw_input('Press any key to the next example')
    print

print 'Thank you'