# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import ast
import util

# <codecell>

from ast import *

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

util.parseprint(code)

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

    def __init__(self, current_class, base_class):
        self.current_class = current_class
        self.base_class = base_class

    def visit_Expr(self, node):
        try:
            if node.value.func.value.func.id is 'super':
                inharite_methods_and_attributes(self.current_class, self.base_class)
        except Exception as e:
            print e
        try:
            if node.value.func.value.id is self.base_class.name:
                inharite_methods_and_attributes(self.current_class, self.base_class)
        except:
            pass


class ClassVisitor(ast.NodeVisitor):

    def __init__(self, current_class, base_class):
        self.current_class = current_class
        self.base_class = base_class
    
    def visit_FunctionDef(self, node):
        if node.name is '__init__':
            for child_node in node.body:
                visitor = InitVisitor(self.current_class, self.base_class)
                visitor.visit(child_node)
        else:
            self.current_class.methods.append(node.name)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        if node.targets[0].value.id is 'self':
            self.current_class.attributes[node.targets[0].attr]=AttributeVisitor().visit(node.value)
        

class ProgramVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        """
        Visitor function used by the NodeVisitor as a callback function which
        is called for every ClassDef instance it encounters.
        :param node: ClassDef node to handle.
        :raise Exception: If the current ClassDef was already declared (and
        parsed) or has multiple inheritance an exception will be thrown.
        """
        if node.name in class_dict:
            raise Exception('Multiple definitions per class are not supported (%s)' % node.name)
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance is not supported (%s)' % node.name)
        
        clazz = ClassRepresentation(node.name)
        visitor = ClassVisitor(clazz, class_dict[node.bases[0].id])
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


