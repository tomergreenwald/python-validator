import logging
logging.basicConfig(level = logging.CRITICAL)
from tabulate import tabulate
class Example(object):
    def __init__(self, code, description, brief):
        self.code = code
        self.desc = description
        self.brief = brief


examples = []

code1 = """
class A(object):
    pass

a = A()
a.a
a.a
"""
examples.append(
    Example(code1, 'Basic example, creates object of type A and state that the object does not have attribute a. '
                   'After the first call to a.a, the validator adds the attribute "a" to the abstract state of the object, '
                   '(We restricting the error to the first occurrence). Therefore, the second call should be valid', \
                   'Basic adaptive attribute'
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
            'The call to a.a should be valid since the attribute exists. '
            'The second assignment should state that "a" does not have attribute "c"', \
            'Basic attribute error'
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
            'This example demonstrates the power of the validator in adding attributes during the fly. '
            'Objects of type A initialized with no attributes. '
            'We add the attribute "m" from the "main" scope, using dot operator, and call to a method that adds attribute '
            '"c" using "self" reference', \
            'Dynamic attributes'
            
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
            'As you can see it simples combined expressions into small and compact ones. '
            'This allows us to focus our efforts in the semantics and not in the syntactics. '
            'In this example we create object "a" of type A and object "b" of type B that holds "a" in the attribute "b". '
            'All the calls in the first group are valid, since all the attributes exists. '
            'In the second group, b.b.b does not exists, so it should raise error. After this statement, '
            'since in the abstract world we have added attribute b to b.b (as stated in the previous examples), '
            'and "a" and "b.b" are the same object, the call to a.b is legal. '
            'In the third group, we add attribute c to a.c, so the validator states that b.b.c exists.', \
            'Simpler in use'
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
            'We create two objects - "b" and "c" that shares the same object "a". '
            'After we add to "a" attribute "d" using b.b.d, that attribute exists in c.c.d as well.', \
            'Complex variables'
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
            'The validator should conclude that a.a and a.b are ints, so the addition operator is valid.', \
            'Addition between numbers'
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
            'Creates object of type A having two attributes, "a" is a string and "b" is a int. '
            'The method isalpha() is a builtin method for strings only. '
            'Therefore the first call should be legal and the second should state that the method does not exists.', \
            'Another builtin functions'
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
            'a.foo_b() should state that "a" does not have method foo_b', \
            'Method calls and builtin functions'
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
            'Demonstrates call from one method to another in the same object.', \
            'Function call inside function call'
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
            'b.a does not exists', \
            'Simple inheritance'
    )
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
            'therefore both b.a and b.b exists. '
            'C does not have a ctor. In this case the super ctor automatically called, therefore c.a exists', \
            'Simple inheritance 2'
    )
)

code111 = """
class A(object):
    def foo_a(self):
        self.a = 2

class B(A):
    pass

b = B()
b.foo_a()

b.a
"""

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
            'List example. The list represented in the abstract world as LUB of the elements, '
            'Easy to see that x.a should be fine and x.b does not exists.', \
            'Simple list'
    )
)

code13 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(object):
    def __init__(self):
        self.a = 1
        self.b = 1

a = A()
b = B()
for x in [a, a, b]:
    x.a
    x.b
    x.c
"""
examples.append(
    Example(code13,
            'List example 2. x.b raised Alert since it does not exists for all the elements, x.c is an error.', \
            'Simple list 2'
    )
)

code14 = """
class A(object):
    def __init__(self):
        self.a = 1

class B(object):
    def __init__(self):
        self.a = 1
        self.b = 1

a1 = A()
a2 = A()
l = [a1, a2]
l.append(B())

for x in l:
    x.a
    x.b
    x.c
"""
examples.append(
    Example(code14,
            'Same example but using append to create the list. '
            'In this case we create the first refer to the list as LUB of "a1" and "a2", '
            'when we call to "append" we LUB the list with B(a1)', \
            'List with append'
    )
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
            'a.b exists just for the else therefore it alert us', \
            'If-Else'
    )
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
            'Advanced If-Else example. '
            'a.a and a.b exists in all the paths, '
            'others may exists depends on the boolean expressions results.', \
            'Advanced If-Else'
    )
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
            'a.a should exists in any case because it will be added in the try part or in the except part. '
            'a.d should exists because it will be added in the finally part. '
            'a.b will be added just if the try part did not raised an exception. '
            'a.c will be added just if the try part raised an exception. '
            'The logic "behind the scene"- '
            'First, evaluate the try block, it is consistent with a state where no exception raised. '
            'Second, evaluate only the except block, it is consistent with a state where the exception thrown raised in the first expression of the try block. '
            'Third, evaluate just the first expression of the try block and the except block, '
            'the first two expressions of the try block and the except block, and so on. '
            'It is consistent with exception raised in any line. '
            'In any case, evaluate the finally part. '
            'Finally - LUB all the abstract states into an abstract state that represent the entire block.', \
            'Try-Except-Finally'
    )
)

code18 = """
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
    Example(code18,
            'Advanced try-except-finally example. '
            'a.a should exists in any case because it will be added in the try part or in the except part. '
            'a.g should exists because is will be added in the finally part. '
            'a.i is added in the finally of the finally part in the try-finally'
            'any other attribute may not exists. It depends where the exception raised (if any).', \
            'Advanced Try-Except-Finally'
    )
)

code19 = """
class A(object):
    pass

def adding_a(x):
    x.a = 1

a = A()
adding_a(a)
a.a
"""
examples.append(
    Example(code19,
            'Calling static functions examples, moving the variables between scopes', \
            'Static function calls'
    )
)

code20 = """
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
    Example(code20,
            'Polymorphism example. a.a.foo exists (no matter if we initialized the object with "b" or "c"), '
            'a.a.b and a.a.c may exists, depends on the boolean expression.', \
            'Polymorphism'
    )
)

code21 = """
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
    Example(code21,
            'Return value example - get_a should return object of type A with two attributes - a and b', \
            'Return value of function'
    )
)

code22 = """
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
    Example(code22,
            'Same example as 13 and 14, but now attribute a has another attribute. Here a weakness of '
            'our abstraction is shown, and we receive an alert for attribute a.', \
            'Complex list with weakness')
)


code23 = """
class A(object):
    def __init__(self):
        self.a = 1

a1 = A()
a2 = a1.foo()

a2.x
a1.x
a1.x.x
"""
examples.append(
    Example(code23,
            'Here is a demonstration for handling unknown functions. We don\'t know what is the '
            'implementation of function "foo", so we return TOP. All possible attributes '
            'of a2 will be legal. After query for a1.x was failed, it is considered as TOP.', \
            'Unknown function calls'
    )
)

code24 = """
class T(object):
    pass

class A(object):
    def __init__(self):
        self.a = 1
    
    def x(self):
        return 1
    
    def y(self):
        return "a"

class B(object):
    def __init__(self):
        self.x = 1
        self.a = 2
    
    def y(self):
        return 4
    
class C(object):
    def __init__(self):
        self.a = T()
        

a = A()
b = B()
c = C()

if True:
    x = a
elif True:
    x = b
else:
    x = c

x.x()
y = x.y()
y.real
x.a.ttt = 5
x.a.rrr = 6

"""
examples.append(
    Example(code24,
            'This exmaple shows the handling of callability and mutability. '
            'x.x() might now exist, and might not be callable. Then, x.y() can return int, '
            'which has attribute "real", or str which hasn\'t attribute "real". '
            'x.a always exists, but might be unmutable. After alert for ttt was '
            'reported, an alert for rrr is not reported (adaptivity of state).', \
            'Callability, mutability and adaptivity')
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

    There are %d examples. Have fun! :)
    """ %len(examples)
    print greetings
    raw_input('Hit any key to start')
    print

    ind = -1
    while True:
        s = raw_input('Press any key to the next example, jmp to (n)th example, (q)uit, (h)elp ')
        print
        if s.lower() == 'q':
            break
        elif s.lower() == 'h':
            print '\n'.join(['%d:\t%s' %(x + 1, examples[x].brief) for x in xrange(len(examples))])
            continue
        try:
            s_ind = int(s)
            if s_ind == 0:
                break
            if s_ind <= 0 or s_ind > len(examples):
                print 'No such example. Enter a number between 1 and %d' %len(examples)
                continue
            ind = s_ind - 1
        except ValueError:
            ind += 1
            if ind >= len(examples):
                break
        
        example = examples[ind]
        print 'Example No. %d' %(ind + 1)
        print '=============='
        print
        print example.desc
        print
        print 'Orignal Code:'
        print '============='
        print example.code
        print
        simple = simpler.make_simple(example.code)
        print 'After the simpling process:'
        print '=============='
        print simple
        print

        ast_tree = ast.parse(simple)
        visitor = ProgramVisitor()
        visitor.visit(ast_tree)
        headers = ["State #", "Action", "From", "To", "Errors"]
        print tabulate(visitor.table, headers,tablefmt="grid")
        for i in xrange(len(visitor.table)):
            visitor.table.pop()

        

    print 'Thank you'


if __name__ == '__main__':
    main()