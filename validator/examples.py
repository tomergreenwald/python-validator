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
    Example(code1, 'Basic example, creates object of type A and state that the object does not have attribute a.'
                   'After the first call to a.a, the validator adds the attribute "a" to the abstract state of the object, '
                   '(We restricting the error to it"s first occurrence). Therefore, the second call should raise no error'
    )
)

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
            'Creates object of type A with attribute a. '
            'The call to a.a should raise no error since the attribute exists. '
            'The second assignment should state that "a" does not have attribute "c"'
    )
)

code9 = """
class A(object):
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
            'This example demonstrates the power of the validator in adding attributes during the fly.'
            'Objects of type A initialized with no attributes. '
            'We add the attribute "m" from the "main" scope, using dot operator, and call to a method that adds attribute '
            '"c" using "self" reference'
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
            'This is the first example we are using the simpler. '
            'As you can see it simples combined expressions into small and compact ones.'
            'This allows us to focus our efforts in the semantics and not in the syntactics.'
            'In this example we create object "a" of type A and object "b" of type B that holds "a" in the attribute "b".'
            'All the calls in the first group are valid, since all the attributes exists.'
            'In the second group, b.b.b does not exists, so it should raise error. After this statement, '
            'since in the abstract world we have added attribute b to b.b (as stated in the previous examples), '
            'and "a" and "b.b" are the same object, the call to a.b is legal.'
            'In the third group, we add attribute c to a.c, so the validator states that b.b.c exists.'
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
            'We create two objects - "b" and "c" that shares the same object "a".'
            'After we add to "a" attribute "d" using b.b.d, that attribute exists in c.c.d as well.'
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
            'The validator should conclude that a.a and a.b are ints, so the addition operator is valid.'
    )
)

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
            'Creates object of type A having two attributes, "a" is a string and "b" is a int.'
            'The method isalpha() is a builtin method for strings only.'
            'Therefore the first call should be legal and the second should state that the method does not exists.'
    )
)

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
            'Creates object of type A, a.foo_a() is a legal call and all the used attributes are legal. '
            'Note that the validator knows that "self" reference "a". '
            'a.foo_c() should state that "a" does not have attribute c. '
            'a.foo_b() should state that "a" does not have method foo_b'
    )
)

code8 = """
class A(object):
    def __init__(self, x):
        self.a = x

    def foo_a(self):
        self._foo_a()

    def _foo_a(self):
        self.a.a = 1

class B(object):
    pass

b = B()
a = A(b)
a.foo_a()
a.a.a
"""
examples.append(
    Example(code8,
            'Demonstrates call from one method to another in the same object.'
    )
)

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
            'Inheritance example - although B extends A, since B did not call to the super ctor, '
            'b.a does not exists')
)

code11 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(A):
    def __init__(self):
        super(B, self).__init__()
        self.b = 2

class C(A):
    pass

b = B()
b.a
b.b

c = C()
c.a
"""
examples.append(
    Example(code11,
            'Inheritance example 2. When we initialized "b" the ctor calls to the super ctor, '
            'therefore both b.a and b.b exists.'
            'C does not have a ctor. In this case the super ctor automatically called, therefore c.a exists ')
)

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
            'List example. The list represented in the abstract world as LUB of the elements,'
            'Easy to see that x.a should be fine and x.b does not exists.')
)

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
for x in [a, a, b]:
    x.a
    x.b
    x.c
"""
examples.append(
    Example(code13,
            'List example 2. x.b raised Alert since it does not exists for all the elements, x.c is an error.')
)

code14 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(object):
    def __init__(self, x):
        self.a = x
        self.b = 1

a1 = A()
a2 = A()
l = [a1, a2]
l.append(B(a1))

for x in l:
    x.a
    x.b
    x.c
"""
examples.append(
    Example(code14,
            'Same example but using append to create the list. '
            'In this case we create the first refer to the list as LUB of "a1" and "a2", '
            'when we call to "append" we LUB the list with B(a1)')
)

code15 = """
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
    Example(code15,
            'If-Else example, we LUBing the IF evaluation with the ELSE evaluation. The result is that a.a always exists. '
            'a.b exists just for the else therefore it alert us')
)

code151 = """
class A(object):
    pass

a = A()

if True:
    a.a = 1

    if True:
        a.b = 2
        a.c = 3
    else:
        a.b = 2
        a.d = 3

    if True:
        a.e = 3
else:
    if True:
        a.a = 1
        a.b = 2
        a.c = 3
    else:
        a.a = 1
        a.b = 2
        a.d = 3

    a.f = 4

a.a
a.b
a.c
a.d
a.e
a.f
"""
examples.append(
    Example(code151,
            'Advanced If-Else example.'
            'a.a and a.b exists in all the paths, '
            'others may exists depends on the boolean expressions results.')
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

a.a
a.b
a.c
"""
examples.append(
    Example(code16,
            'Try-Except example. ')
)

code17 = """
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
    Example(code17,
            'Try-Except-Finally example.'
            'a.a should exists in any case because it will be added in the try part or in the except part.'
            'a.d should exists because is will be added in the finally part.'
            'a.b will be added just if the try part did not raised an exception.'
            'a.c will be added just if the try part raised an exception.')
)

code17 = """
class A(object):
    pass

a = A()
try:
    a.a = 2
    a.b = 3

    try:
        a.c = 1
    finally:
        a.d = 2
except Exception:
    a.a = 2
    a.e = 3
except Exception:
    a.a = 2
    a.f = 2
finally:
    a.g = 2

    try:
        a.h = 1
    finally:
        a.i = 2

a.a
a.b
a.c
a.d
a.e
a.f
a.g
a.h
a.i
"""
examples.append(
    Example(code17,
            'Advanced try-except-finally example.'
            'a.a should exists in any case because it will be added in the try part or in the except part.'
            'a.g should exists because is will be added in the finally part.'
            'a.i is added in the finally of the finally part in the try-finally'
            'any other attribute may not exists. It depends where the exception raised (if any).')
)

code18 = """
class A(object):
    pass

def adding_a(x):
    x.a = 1

a = A()
adding_a(a)
a.a
"""
examples.append(
    Example(code18,
            'Calling static functions examples, moving the variables between scopes')
)

code19 = """
class A(object):
    def __init__(self, x):
        self.a = x

class B(object):
    def foo(self):
        self.b = 2

class C(object):
    def foo(self):
        self.c = 2

b = B()
c = C()

if True:
    a = A(b)
else:
    a = A(c)

a.a.foo()

a.a.b
a.a.c
"""
examples.append(
    Example(code19,
            'Polymorphism example. a.a.foo exists (no matter if we initialized the object with "b" or "c"),'
            'a.a.b and a.a.c may exists, depends on the boolean expression.')
)

code20 = """
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
examples.append(
    Example(code20,
            'Return value example - get_a should return object of type A with two attributes - a and b')
)

import ast

from validator.visitors.Visitors import ProgramVisitor
from validator.simplers import simpler


def main():
    greetings = """
    Welcome to the python attribute validator examples!
    Any example starts with short description, continues with the code that will be checked, and the code after the simpler methods.
    Next, the code will run through the validatior.

    Note that we only demonstrate some core features. Full description of the validator capacity is in the doc.

    There are 22 examples. Have fun! :)
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


if __name__ == '__main__':
    main()