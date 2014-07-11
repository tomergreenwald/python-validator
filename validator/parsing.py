__author__ = 'Oded'

import ast


class ClassRepresentation(object):
    def __init__(self, name, base):
        self.name = name
        self.base = base
        self.methods = []
        self.attributes = {}

    def __repr__(self):
        return '<Class %s, base: %s, methods: %s, attributes: %s>' % \
               (self.name, 'none' if self.base is None else self.base.name, self.methods, self.attributes)

    def inherit(self, other):
        for m in other.methods:
            self.methods.append(m)
        for a, t in other.attributes.iteritems():
            self.attributes[a] = t


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
            raise Exception('Class not found') # Maybe should be object?
        return class_dict[node.func.id]


class InitVisitor(ast.NodeVisitor):
    current_class = None

    def visit_Expr(self, node):
        try:
            if node.value.func.attr is '__init__':
                try:
                    if node.value.func.value.func.id is 'super':
                        InitVisitor.current_class.inherit(class_dict[node.value.func.value.args[0].id].base)
                except AttributeError as e:
                    pass

                try:
                    if node.value.func.value.id in class_dict:
                        InitVisitor.current_class.inherit(class_dict[node.value.func.value.id])
                except AttributeError as e:
                    pass
        except Exception as e:
            raise Exceptio__author__ = 'Oded'

import ast


class MethodRepresentation(object):
    def __init__(self, name):
        self.name = name
        self.arguments = {}

    def __repr__(self):
        return '<Method %s, arguments: %s>' % (self.name, self.arguments)


class ClassRepresentation(object):
    def __init__(self, name, base):
        self.name = name
        self.base = base
        self.methods = []
        self.static_methods = []
        self.attributes = {}

        if self.name is not 'object':
            self.inherit(class_dict['object'])

    def __repr__(self):
        return '<Class %s, base: %s, methods: %s, static_methos: %s, attributes: %s>' % \
               (self.name, 'none' if self.base is None else self.base.name, self.methods, self.static_methods, self.attributes)

    def inherit(self, other):
        for m in other.methods:
            self.methods.append(m)
        for a, t in other.attributes.iteritems():
            self.attributes[a] = t


class AttributeVisitor(ast.NodeVisitor):
    def visit_Str(self, node):
        return 'str'

    def visit_Num(self, node):
        return 'num'

    def visit_Name(self, node):
        if node.id is 'None':
            return 'NoneType'
        if node.id in ['True', 'False']:
            return 'bool'
        return node.id

    def visit_List(self, node):
        return 'list'

    def visit_Tuple(self, node):
        return 'tuple'

    def visit_Dict(self, node):
        return 'dict'

    def visit_Call(self, node):
        if node.func.id is 'set':
            return 'set'

        if node.func.id not in class_dict.keys():
            raise Exception('Class not found') # Maybe should be object?
        return class_dict[node.func.id]


class ClassVisitor(ast.NodeVisitor):
    current_class = None

    def visit_FunctionDef(self, node):
        m = MethodRepresentation(node.name)

        args = [a.id for a in node.args.args]
        if len(args) > 0 and args[0] is 'self':
            static = False
            args = args[1:]
        else:
            static = True

        defaults = node.args.defaults
        for i in xrange(len(args) - len(defaults)):
            m.arguments[args[i]] = None
        for i in xrange(len(defaults)):
            m.arguments[args[-len(defaults):][i]] = AttributeVisitor().visit(defaults[i])

        if not static:
            self.current_class.methods.append(m)
        else:
            self.current_class.static_methods.append(m)

        self.generic_visit(node)

    def visit_Assign(self, node):
        if node.targets[0].value.id is 'self':
            self.current_class.attributes[node.targets[0].attr]=AttributeVisitor().visit(node.value)

    def visit_Expr(self, node):
        try:
            if node.value.func.attr is '__init__':
                try:
                    if node.value.func.value.func.id is 'super':
                        self.current_class.inherit(class_dict[node.value.func.value.args[0].id].base)
                except AttributeError as e:
                    pass

                try:
                    if node.value.func.value.id in class_dict:
                        self.current_class.inherit(class_dict[node.value.func.value.id])
                except AttributeError as e:
                    pass
        except Exception as e:
            raise Exception('Not a standart ctor')


class ProgramVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if node.name in class_dict:
            raise Exception('Double definition of class %s' % node.name)
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)

        class_dict[node.name] = ClassRepresentation(node.name, class_dict[node.bases[0].id])
        visitor = ClassVisitor()
        ClassVisitor.current_class = class_dict[node.name]
        visitor.visit(node)


class_dict = {}


def get_defined_classes(code):
    class_dict['object'] = ClassRepresentation('object', None)
    class_dict['Excption'] = ClassRepresentation('Exception', class_dict['object'])

    ast_tree = ast.parse(code)
    ProgramVisitor().visit(ast_tree)

    for c in class_dict.values():
        c.methods = list(set(c.methods))

    return class_dict

def get_parsed_code(code):
    raise NotImplementedError()

get_defined_classes(code)

for n, c in class_dict.items():
    print cn('Not a standart ctor')


class ClassVisitor(ast.NodeVisitor):
    current_class = None

    def visit_FunctionDef(self, node):
        if node.name is '__init__':
            for child_node in node.body:
                visitor = InitVisitor()
                InitVisitor.current_class = ClassVisitor.current_class
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
            raise Exception('Double definition of class %s' % node.name)
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)

        class_dict[node.name] = ClassRepresentation(node.name, class_dict[node.bases[0].id])
        visitor = ClassVisitor()
        ClassVisitor.current_class = class_dict[node.name]
        visitor.visit(node)


class_dict = {}


def get_defined_classes(code):
    class_dict['object'] = ClassRepresentation('object', None)
    class_dict['Excption'] = ClassRepresentation('Exception', class_dict['object'])

    ast_tree = ast.parse(code)
    ProgramVisitor().visit(ast_tree)

    for c in class_dict.values():
        c.methods = list(set(c.methods))

    return class_dict

def get_class_attributes(class_name):   # FOR TOMER
    """
    Return the requested class attributes
    """
    raise NotImplementedError()