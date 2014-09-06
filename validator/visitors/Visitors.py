import ast

from validator.state.abs_state import AbstractState
from validator.representation.ClassRepresentation import ClassRepresentation


class Frame(object):
    def __init__(self, frame_name):
        self.frame_name = frame_name
        self.variables = []

    def register(self, variable):
        self.variables.append(variable)

    def clear(self, abstract_state):
        for variable in self.variables:
            abstract_state.forget_var(self.frame_name + "#" + variable)


class Stack(object):
    def __init__(self):
        self.frames = [Frame("root")]

    def insert(self, frame):
        self.frames.append(frame)

    def pop(self, abstract_state):
        frame = self.frames.pop()
        frame.clear(abstract_state)

    def frame_names(self, level=0):
        names = []
        for frame in self.frames:
            names.append(frame.frame_name)
        if level == 0:
            return names
        else:
            return names[:-level]

    def current_frame(self):
        return self.frames[-1]

    def __len__(self):
        return len(self.frames)


def get_node_name(node):
    """
    Generates the fully qualified name for a given node. If the node contains a 'value' attribute then it is a complex
    node and we need to generate its name recursively. Otherwise it either has an 'attr' value or an 'id' value which
    are the node's name (depends on whether the node represents an attribute or a variable).
    """
    if hasattr(node, 'value'):
        return get_node_name(node.value) + '.' + node.attr
    if hasattr(node, 'attr'):
        return node.attr
    return node.id


def var_name_list(stack, var, level=0):
    """
    Generates a list of probable variable names according to the given stack and variable.
    :param stack: Current stack.
    :param var: Variable name.
    :return: List of probable names.
    """
    names = []
    if len(stack) > 1:
        function_name = "#".join(stack.frame_names(level))
        names.append(function_name + "#" + var)
    names.append("root#" + var)
    return names


def actual_var_name(stack, var, level=0):
    """
    Generates a fully qualified name for a local or a global variable.
    Throws exception if the variable was no previously set to the abstract state.
    :param stack: Current stack.
    :param abstract_state: Current AbstractState.
    :param var: Variable name.
    :return: Fully qualified variable name.
    """
    if var in stack.frames[-(level + 1)].variables:
        return stack.frames[-(level + 1)].frame_name + "#" + var
    if var in stack.frames[0].variables:
        return stack.frames[0].frame_name + "#" + var
    raise Exception("Referenced variable was not assigned previuosly - [%s] - %s" % (str(stack.frame_names()), var))


def stack_var_name(stack, var, level=0):
    """
    Generates a fully qualified name for a variable on the stack.
    :param stack: Current stack.
    :param var: Variable name.
    :return: Fully qualified variable name.
    """
    return var_name_list(stack, var, level)[0]


def register_assignment(stack, abstract_state, from_var, to_var_name, split_stack=False, new_object=None):
    """
    Registers an assignment from one variable (or const value) to another to a given AbstractState.
    :param abstract_state: AbstractState to register assignment to.
    :param from_var: AST node to extract type and data from.
    :param to_var_name: variable name to assign data to.
    """
    stack.current_frame().register(to_var_name)
    actual_to_name = actual_var_name(stack, to_var_name)
    if split_stack:
        level = 1
    else:
        level = 0
    if type(from_var) is ast.Name or type(from_var) is ast.Attribute:
        if from_var.id is "ret_val":
            actual_from_name = "ret_val"
        else:
            actual_from_name = actual_var_name(stack, from_var.id, level)
        abstract_state.set_var_to_var(actual_to_name, actual_from_name)
        print "assigned {from_var} to {to_var}".format(from_var=actual_from_name, to_var=actual_to_name)
    elif from_var is not None:
        if type(from_var) is ast.Tuple:
            abstract_state.set_var_to_const(actual_to_name, tuple())
            print "assigned {var_type} to {to_var}".format(var_type=tuple(),
                                                           to_var=actual_to_name)
        elif type(from_var) is ast.Dict:
            abstract_state.set_var_to_const(actual_to_name, dict())
            print "assigned {var_type} to {to_var}".format(var_type=dict(),
                                                           to_var=actual_to_name)
        else:
            abstract_state.set_var_to_const(actual_to_name, getattr(from_var, from_var._fields[0]))
            print "assigned {var_type} to {to_var}".format(var_type=type(getattr(from_var, from_var._fields[0])),
                                                           to_var=actual_to_name)
    else:
        abstract_state.set_var_to_const(actual_to_name, new_object)
        print "assigned {var_type} to {to_var}".format(var_type=type(new_object), to_var=actual_to_name)


def handle_kwargs(abstract_state, args, function, keywords, stack):
    arguments = []
    for i in xrange(len(args)):
        arguments.append(i)
        register_assignment(stack, abstract_state, args[i], function.args.args[i].id, True)
    for i in xrange(len(function.args.defaults)):
        arg_index = i + len(function.args.args) - len(function.args.defaults)
        arg = function.args.args[arg_index]
        found = False
        for keyword in keywords:
            if arg.id == keyword.arg:
                found = True
                register_assignment(stack, abstract_state, keyword.value, keyword.arg, True)
        if not found:
            default = function.args.defaults[i]
            register_assignment(stack, abstract_state, default, function.args.args[arg_index].id, True)


def evaluate_function(function, args, keywords, stack, abstract_state, functions):
    stack.insert(Frame(function.name))
    handle_kwargs(abstract_state, args, function, keywords, stack)
    assess_list(function.body, stack, abstract_state, functions)
    stack.pop(abstract_state)


class CallVisitor(ast.NodeVisitor):
    def __init__(self, stack, abstract_state, functions, classes, name=None):
        super(CallVisitor, self).__init__()
        self.name = name
        self.abstract_state = abstract_state
        self.stack = stack
        self.functions = functions
        self.classes = classes

    def visit_Call(self, node):
        if type(node.func) is ast.Name:
            function_name = node.func.id
            if function_name in self.classes:
                init_object(self.name, self.abstract_state, self.classes[function_name], node.args, node.keywords,
                            self.stack,
                            self.functions)
            elif function_name in self.functions:
                evaluate_function(self.functions[node.func.id], node.args, node.keywords, self.stack,
                                  self.abstract_state,
                                  self.functions)
            else:
                raise Exception('Class or function not found %s' % (node.func.id))  # Maybe should be top?

        elif type(node.func) is ast.Attribute:
            function_name = node.func.attr
            _self = node.func.value.id
            #should return a list of contexts saved for each method (one per method impl)
            methods = self.abstract_state.get_method_data(_self, function_name)
            if len(methods) > 0:
                abstract_state_clean = self.abstract_state.clone()
                for method in methods:
                    abstract_state_cpy = abstract_state_clean.clone()
                    evaluate_function(method, [ast.Name(id=_self)] + node.args, node.keywords, self.stack,
                                      abstract_state_cpy,
                                      self.functions)
                    self.abstract_state.lub(abstract_state_cpy)
            else:
                raise Exception(
                    'Method {method} was called for {obj}, but no implementation exists'.format(method=function_name,
                                                                                                obj=_self))
        else:
            raise Exception("not supported")

        if self.name and self.abstract_state.has_var("ret_val"):
            register_assignment(self.stack, self.abstract_state, ast.Name(id="ret_val"), self.name)
            #self.abstract_state.set_var_to_var(actual_var_name(self.stack, self.name), "ret_val")
            self.abstract_state.forget_var("ret_val")


class AssignVisitor(CallVisitor):
    def __init__(self, name, stack, abstract_state, functions, classes):
        """
        Handle assign calls. Adds to the object the relavent methods and attributes
        """
        super(AssignVisitor, self).__init__(stack, abstract_state, functions, classes, name=name)

    def visit_Attribute(self, node):
        """
        example: x = y.a

        Handles attribute node.
        :param node: Attribute Node.
        """
        self.abstract_state.set_var_to_var(self.name,
                                           actual_var_name(self.stack, node.value.id) + "." + node.attr)

    def visit_Str(self, node):
        """
        Handles string node.
        :param node: String Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)

    def visit_Num(self, node):
        """
        Handles number node.
        :param node: Number Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)

    def visit_Name(self, node):
        """
        Handles name node (It means that we assign one variable to another - copy their pointers)..
        :param node: Name Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)

    def visit_List(self, node):
        """
        Handles list node.
        :param node: List Node.
        """
        # TODO handle + and 'append' - should change the lub
        # TODO handle Subscript should do the logic on 'var_that_represents_the_list_items'
        register_assignment(self.stack, self.abstract_state, node, self.name)  # Register the name as list

        list_lub = self.name + '_vars_lub'

        if node.elts:
            register_assignment(self.stack, self.abstract_state, node.elts[0], list_lub)
        for item in node.elts[1:]:
            clone = self.abstract_state.clone()
            register_assignment(self.stack, clone, item, list_lub)
            self.abstract_state.lub(clone)

    def visit_Tuple(self, node):
        """
        Handles tuple node.
        :param node: Tuple Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)  # Register the name as tuple

        tuple_lub = self.name + '_vars_lub'

        if node.elts:
            register_assignment(self.stack, self.abstract_state, node.elts[0], tuple_lub)
        for item in node.elts[1:]:
            clone = self.abstract_state.clone()
            register_assignment(self.stack, clone, item, tuple_lub)
            self.abstract_state.lub(clone)

    def visit_Dict(self, node):
        """
        Handles dictionary node.
        :param node: Dictionary Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)

        keys_lub = self.name + '_keys_lub'
        if node.keys:
            register_assignment(self.stack, self.abstract_state, node.keys[0], keys_lub)
        for item in node.keys[1:]:
            clone = self.abstract_state.clone()
            register_assignment(self.stack, clone, item, keys_lub)
            self.abstract_state.lub(clone)

        values_lub = self.name + '_values_lub'
        if node.values:
            register_assignment(self.stack, self.abstract_state, node.values[0], values_lub)
        for item in node.values[1:]:
            clone = self.abstract_state.clone()
            register_assignment(self.stack, clone, item, values_lub)
            self.abstract_state.lub(clone)


class ExprVisitor(CallVisitor):
    def __init__(self, stack, abstract_state, functions, classes):
        super(ExprVisitor, self).__init__(stack, abstract_state, functions, classes)


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def visit_FunctionDef(self, node):
        self.context[node.name] = node


def initialize_abstract_state(abstract_state):
    abstract_state.set_var_to_const('root#True', True)
    abstract_state.set_var_to_const('root#False', False)
    abstract_state.set_var_to_const('root#None', None)


class ClassDefVisitor(ast.NodeVisitor):
    """
    Handles class definitions. Creates new class in classes dictionary and set it's name,
    super class, methods and statics
    """

    def __init__(self, classes):
        super(ClassDefVisitor, self).__init__()
        self.clazz = None
        self.classes = classes

    def visit_ClassDef(self, node):
        if node.bases[0].id == 'object':
            self.clazz = ClassRepresentation(node.name, node.bases[0].id)
        else:
            if node.bases[0].id not in self.classes:
                raise Exception('Can not find super class')     # Compile error or init from outer library
            self.clazz = ClassRepresentation(node.name, self.classes[node.bases[0].id])
        self.classes[node.name] = self.clazz
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # FunctionDefVisitor(self.functions).visit(node)
        args = [a.id for a in node.args.args]

        if args and args[0] is 'self':
            self.clazz.methods[node.name] = node
        else:
            self.clazz.static_methods[node.name] = node

    def visit_Assign(self, node):
        # TODO - won't compile, number of arguments doesn't fit
        # TODO - things should be consist with the stack
        handle_assign(node, self.clazz.static_vars)


class ProgramVisitor(ast.NodeVisitor):
    def __init__(self, stack=None, abstract_state=None, functions={}, classes={}):
        """
        Should visit all the program
        """
        super(ProgramVisitor, self).__init__()
        if not abstract_state:
            self.abstract_state = AbstractState()
            initialize_abstract_state(self.abstract_state)
        else:
            self.abstract_state = abstract_state
        if stack:
            self.stack = stack
        else:
            self.stack = Stack()
        self.functions = functions
        self.classes = classes
        self.return_value = None

    def visit_ClassDef(self, node):
        # """
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)
        ClassDefVisitor(self.classes).visit(node)
        #"""
        #raise Exception('Call visit is not supported yet')

    def visit_FunctionDef(self, node):
        FunctionDefVisitor(self.functions).visit(node)

    def visit_Expr(self, node):
        ExprVisitor(self.stack, self.abstract_state, self.functions, self.classes).visit(node)

    def visit_Assign(self, node):
        """
        Handles assignment to variable.
        :param node: Current assignment node.
        """
        handle_assign(node, self.stack, self.abstract_state, self.functions, self.classes)

    def visit_For(self, node):
        """
        Handles for loop.
        The iterate var is already should be in LUB form. We just need to assess the body of the loop (and set the iter key).
        """
        register_assignment(self.stack, self.abstract_state, node.iter + '_vars_lub', node.target.id)
        assess_list(node.body, self.stack, self.abstract_state, self.functions)

    def visit_If(self, node):
        """
        Handles if/elif/else cases by assessing every option and than calculating the Least Upper Bound for them all.
        :param node: Current if node.
        """
        if not node.orelse:
            before_if_states = self.abstract_state.clone()
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            self.abstract_state.lub(before_if_states)
        else:
            orelse_state = self.abstract_state.clone()
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            assess_list(node.orelse, self.stack, orelse_state, self.functions)
            self.abstract_state.lub(orelse_state)

    def visit_TryFinally(self, node):
        before_block_abstract_states = self.abstract_state.clone()
        helper = []
        for expr in node.body:
            helper.append(expr)
            current_abstract_states = before_block_abstract_states.clone()
            assess_list(helper, self.stack, current_abstract_states, self.functions)
            self.abstract_state.lub(current_abstract_states)
        assess_list(node.finalbody, self.abstract_state, self.functions, self.functions)

    def visit_TryExcept(self, node):
        before_block_abstract_states = self.abstract_state.clone()

        # If no exception raises
        try_block = node.body
        try_block_abstract_states = before_block_abstract_states.clone()
        assess_list(try_block, self.stack, try_block_abstract_states, self.functions)
        self.abstract_state.lub(try_block_abstract_states)

        # If exception raises during the execution
        helper = []
        for expr in try_block:
            helper.append(expr)
            current_abstract_states = before_block_abstract_states.clone()
            assess_list(helper, self.stack, current_abstract_states, self.functions)

            for handler in node.handlers:
                self.abstract_state.set_var_to_const(handler.name.id, 'exception')
                handler_abstract_states = current_abstract_states.clone()
                assess_list(handler.body, self.stack, handler_abstract_states, self.functions)
                self.abstract_state.lub(handler_abstract_states)

    def visit_Return(self, node):
        to_name = actual_var_name(self.stack, getattr(node.value, node.value._fields[0]))
        if self.abstract_state.has_var('ret_val'):
            temp_state = self.abstract_state.clone()
            temp_state.set_var_to_var('ret_val', to_name)
            self.abstract_state.lub(temp_state)
        else:
            self.abstract_state.set_var_to_var('ret_val', to_name)
        print "assigned {from_var} to {to_var}".format(from_var=to_name, to_var="ret_val")


def assess_list(entries, stack, abstract_state, functions):
    """
    Generates a ProgramVisitor and runs it through the given set of entries while updating the given AbstractState.
    :param entries: A list of entries to process.
    :param abstract_state: AbstractState to initialize the ProgramVisitor with.
    """
    visitor = ProgramVisitor(stack, abstract_state, functions)
    for entry in entries:
        visitor.visit(entry)


def handle_assign(node, stack, abstract_state, functions, classes):
    """
    Handles assign - creates the relevant object and connects it to the context.
    """
    if len(node.targets) is not 1:
        # The simpler simples it
        raise Exception('Multiple targets does not supported (%s)' % node.name)

    assign_visitor = AssignVisitor(get_node_name(node.targets[0]), stack, abstract_state, functions, classes)
    assign_visitor.visit(node.value)


def init_object(target, abstract_state, clazz, args, keywords, stack, functions):
    """
    :param clazz: The ClassRepresentation of the class
    """
    #abstract_state.set_var_to_const(actual_var_name(stack, target), object())
    register_assignment(stack, abstract_state, None, target, new_object=object())

    iter_clazz = clazz
    while iter_clazz is not 'object' and '__init__' not in iter_clazz.methods:
        iter_clazz = iter_clazz.base
    if iter_clazz is not 'object':
        evaluate_function(iter_clazz.methods['__init__'], [target] + args, keywords, stack, abstract_state, functions)

    for method in clazz.methods.values():
        abstract_state.set_method_to_var(actual_var_name(stack, target), method)