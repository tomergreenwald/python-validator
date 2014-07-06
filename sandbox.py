# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import ast

# <codecell>

from ast import *

def dump(node, annotate_fields=True, include_attributes=False, indent='  '):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, AST):
            fields = [(a, _format(b, level)) for a, b in iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)
    
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)

def parseprint(code, filename="<string>", mode="exec", **kwargs):
    """Parse some code from a string and pretty-print it."""
    node = parse(code, mode=mode)   # An ode to the code
    print(dump(node, **kwargs))

# <codecell>

code = """
class A(object):
    def __init__(self):
        self.x = 5
        
class B(A):
    def __init__(self):
        super(B, self).__init__()
        A.__init__(self)
"""

# <codecell>

parseprint(code)

# <codecell>

tree = ast.parse(code)

# <codecell>

def inharite_methods_and_attributes(clazz, base):
    for m in base.methods:
        clazz.methods.append(m)
    for a, t in base.attributes.iteritems():
        clazz.attributes[a] = t

class MultipleNameDefenition(Exception):
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return 'Validator does not support multiple definitons with the same name (%s)' % self.name
        

class ClassRepresentation(object):
    def __init__(self, name):
        self.name = name
        self.methods = []
        self.attributes = {}
        
    def __repr__(self):
        return '<Class %s, methods: %s, attributes: %s>' % (self.name, self.methods, self.attributes)
    
    
class AttributeVisitor(ast.NodeVisitor):
    def visit_Str(self, node):
        return 'str'
    
    def visit_Num(self, node):
        return 'num'
    
    def visit_Name(self, node):
        if node.id is 'None':
            return 'NoneType'
        else:
            return 'bool'
        
    def visit_List(self, node):
        return 'list'
    
    def visit_Tuple(self, node):
        return 'tuple'
    
    def visit_Call(self, node):
        if node.func.id is 'set':
            raise Exception('Set is not supported')
        if node.func.id not in class_dict.keys():
            raise Excpetion()
        return class_dict[node.func.id]
    
    
class InitVisitor(ast.NodeVisitor):
    current_class = None
    base_class = None
    
    def visit_Expr(self, node):
        try:
            if node.value.func.value.func.id is 'super':
                inharite_methods_and_attributes(InitVisitor.current_class, InitVisitor.base_class)
        except Exception as e:
            print e
        try:
            if node.value.func.value.id is InitVisitor.base_class.name:
                inharite_methods_and_attributes(InitVisitor.current_class, InitVisitor.base_class)
        except:
            pass


class ClassVisitor(ast.NodeVisitor):
    current_class = None
    base_class = None
    
    def visit_FunctionDef(self, node):
        if node.name is '__init__':
            for child_node in node.body:
                visitor = InitVisitor()
                InitVisitor.current_class = ClassVisitor.current_class
                InitVisitor.base_class = ClassVisitor.base_class
                visitor.visit(child_node)
        else:
            self.current_class.methods.append(node.name)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        if node.targets[0].value.id is 'self':
            self.current_class.attributes[node.targets[0].attr]=AttributeVisitor().visit(node.value)
        

class ProgramVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if node.name in class_dict:
            raise DoubleDefenition(node.name)
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)
        
        clazz = ClassRepresentation(node.name)
        visitor = ClassVisitor()
        ClassVisitor.current_class = clazz
        ClassVisitor.base_class = class_dict[node.bases[0].id]
        visitor.visit(node)
        class_dict[node.name] = clazz
    
    
class_dict = {}

class_dict['object'] = ClassRepresentation('object')
class_dict['Excption'] = ClassRepresentation('Exception')

ast_tree = ast.parse(code)
ProgramVisitor().visit(ast_tree)

for c in class_dict.values():
    c.methods = list(set(c.methods))

for c in class_dict.values():
    print c

# <codecell>

class A(object):
    def __init__(self):
        self.x = 5
        
    def a(self):
        pass

class B(A):
    def __init__(self):
        super(B, self).__init__()
        self.y = 3

# <codecell>

b = B()

# <codecell>

dir({})

# <codecell>


