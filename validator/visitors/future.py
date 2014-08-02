import ast
from validator.representation.ClassRepresentation import ClassRepresentation
from validator.representation.MethodRepresentation import MethodRepresentation
from validator.visitors.Visitors import handle_assign, AssignVisitor

classes = {}
functions = {}

class CallFunction(ast.NodeVisitor):
    def __init__(self, method, args, kwargs):
        super(CallFunction, self).__init__()
        self.varz = {}

        for i in xrange(len(args)):
            self.varz[method.arguments[i].name] = args[i]
            # Handle kwargs
            # Should replace the parameters with the right values by changing the tree

    def visit_FunctionDef(self, node):
        self.generic_visit(node)

    def visit_Assign(self, node):
        handle_assign(node, self.varz)

    def visit_Expr(self, node):
        try:
            if node.value.func.attr is '__init__':
                try:
                    if node.value.func.value.func.id is 'super':
                        self.varz['self'].inherit(classes[classes[node.value.func.value.args[0].id].base],
                                                  node.value.args, node.value.keywords)
                except:
                    pass

                try:
                    if node.value.func.value.id in classes:
                        self.varz['self'].inherit(classes[node.value.func.value.id],
                                                  node.value.args, node.value.keywords)
                except Exception as e:
                    print e
        except:
            pass


class ClassDefVisitor(ast.NodeVisitor):
    """
    Handles class definitions. Creates new class in classes dictionary and set it's name,
    super class, methods and statics
    """

    def __init__(self):
        super(ClassDefVisitor, self).__init__()
        self.clazz = None

    def visit_ClassDef(self, node):
        self.clazz = ClassRepresentation(node.name, node.bases[0].id)
        classes[node.name] = self.clazz
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        m = MethodRepresentation(node.name, node)

        args = [a.id for a in node.args.args]
        defaults = node.args.defaults
        for i in xrange(len(args) - len(defaults)):
            obj = ObjectRepr(args[i])
            obj.simple = object
            m.arguments.append(obj)
        for i in xrange(len(defaults)):
            obj = ObjectRepr(args[-len(defaults):][i])
            AssignVisitor(obj).visit(defaults[i])
            m.arguments.append(obj)

        if len(args) > 0 and args[0] is 'self':
            self.clazz.methods[node.name] = m
        else:
            self.clazz.static_methods[node.name] = m

    def visit_Assign(self, node):
        handle_assign(node, self.clazz.static_vars)


def call_function(method, args, kwargs):
    CallFunction(method, args, kwargs).visit(method.code)


def init_object(obj, clazz, args, kwargs):
    """
    Called when init an object.
    It append the relevant statics and calls to the init method
    """
    obj.static_methods = clazz.static_methods
    obj.static_vars = clazz.static_vars
    obj.methods = clazz.methods
    call_function(obj.methods['__init__'], [obj] + args, kwargs)


class ObjectRepr(object):
    def __init__(self, name=None):
        self.name = name
        self.methods = {}
        self.attributes = {}
        self.static_methods = {}
        self.static_vars = {}
        self.simple = None  # This is just tmp! should use attributes and methods only

    def __repr__(self):
        return '<Object %s: %s, attributes: %s, simple: %s>' % (self.name, self.simple, self.attributes, self.simple)

    def inherit(self, super_class, args, kwargs):
        for m in super_class.methods:
            if m not in self.methods:
                self.methods[m] = super_class.methods[m]
        call_function(classes[super_class.name].methods['__init__'], [self] + args, kwargs)