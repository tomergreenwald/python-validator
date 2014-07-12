import ast

class MethodRepresentation(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.arguments = []

    def __repr__(self):
        return '<Method %s, arguments: %s>' % (self.name, self.arguments)


class ClassRepresentation(object):
    def __init__(self, name, base=None):
        self.name = name
        self.base = base
        self.methods = {}
        self.static_methods = {}
        self.static_vars = {}

    def __repr__(self):
        return '<Class %s, base: %s, methods: %s, static_methos: %s, static_vars: %s' % \
               (self.name, self.base, self.methods, self.static_methods, self.static_vars)

class ObjectRepr(object):
    def __init__(self, name=None):
        self.name = name
        self.methods = {}
        self.attributes = {}
        self.static_methods = {}
        self.static_vars = {}
        self.simple = None

    def __repr__(self):
        return '<Object %s: %s, attributes: %s, simple: %s>' % (self.name, self.simple, self.attributes, self.simple)

    def inherit(self, super_class, args, kwargs):
        for m in super_class.methods:
            if m not in self.methods:
                self.methods[m] = super_class.methods[m]
        call_function(classes[super_class.name].methods['__init__'], [self] + args, kwargs)


class AssignVisitor(ast.NodeVisitor):
    """
    Handle assign calls. Adds to the object the relavent methods and attributes
    """
    def __init__(self, obj):
        super(AssignVisitor, self).__init__()
        self.obj = obj

    def visit_Str(self, node):
        self.obj.simple = 'str'

    def visit_Num(self, node):
        self.obj.simple = 'num'

    def visit_Name(self, node):
        if node.id is 'None':
            self.obj.simple = 'NoneType'
        if node.id in ['True', 'False']:
            self.obj.simple = 'bool'
        self.obj.simple = node.id

    def visit_List(self, node):
        self.obj.simple = 'list'

    def visit_Tuple(self, node):
        self.obj.simple = 'tuple'

    def visit_Dict(self, node):
        self.obj.simple = 'dict'

    def visit_Call(self, node):
        if node.func.id is 'set':
            self.obj.simple = 'set'

        if node.func.id not in classes:
            raise Exception('Class not found') # Maybe should be top?
        init_object(self.obj, classes[node.func.id], node.args, node.keywords)
        # node.func.id can be in functions or something like that


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


class ProgramVisitor(ast.NodeVisitor):
    """
    Should visit all the program
    """
    def visit_ClassDef(self, node):
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)
        ClassDefVisitor().visit(node)

    def visit_Assign(self, node):
        handle_assign(node, varz)


def init_object(obj, clazz, args, kwargs):
    """
    Called when init an object.
    It append the relevant statics and calls to the init method
    """
    obj.static_methods = clazz.static_methods
    obj.static_vars = clazz.static_vars
    obj.methods = clazz.methods
    call_function(obj.methods['__init__'], [obj] + args, kwargs)


def call_function(method, args, kwargs):
    CallFunction(method, args, kwargs).visit(method.code)


def handle_assign(node, context):
    """
    Handles assign - creates the relavent object and connects it to the context.
    """
    if len(node.targets) is not 1:
        raise Exception('Multiple targets does not supported (%s)' % node.name)

    obj = ObjectRepr()
    assign_visitor = AssignVisitor(obj)
    assign_visitor.visit(node.value)

    if isinstance(node.targets[0], ast.Attribute):
        obj.name = node.targets[0].attr
        context[node.targets[0].value.id].attributes[obj.name] = obj
    else:
        obj.name = node.targets[0].id
        context[node.targets[0].id] = obj


classes = {}
varz = {}

ast_tree = ast.parse(code)
visitor = ProgramVisitor()
visitor.visit(ast_tree)