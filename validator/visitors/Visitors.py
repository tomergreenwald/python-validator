import ast

from validator.state.abs_state import AbstractState


def get_variable_name(stack, abstract_state, name):
    fully_qualizfied_name = "#".join(stack).append("_" + name)
    if abstract_state.has_var(fully_qualizfied_name):
        return fully_qualizfied_name
    elif abstract_state.has_var(name):
        return name
    else:
        raise Exception('Name (%s) is not a local or a global variable for the stack - %s' % name, stack)

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


def var_name_list(stack, var):
    """
    Generates a list of probable variable names according to the given stack and variable.
    :param stack: Current stack.
    :param var: Variable name.
    :return: List of probable names.
    """
    names = []
    if (len(stack) > 0):
        function_name = "#".join(stack)
        names.append(function_name + "#" + var)
    names.append(var)
    return names


def actual_var_name(stack, abstract_state, var):
    """
    Generates a fully qualified name for a local or a global variable.
    Throws exception if the variable was no previously set to the abstract state.
    :param stack: Current stack.
    :param abstract_state: Current AbstractState.
    :param var: Variable name.
    :return: Fully qualified variable name.
    """
    names = var_name_list(stack, var)
    for name in names:
        if abstract_state.has_var(name):
            return name
    raise Exception("Refereneced variable was not assigned previuosly - [%s] - %s" %(str(stack), var))

def stack_var_name(stack, var):
    """
    Generates a fully qualified name for a variable on the stack.
    :param stack: Current stack.
    :param var: Variable name.
    :return: Fully qualified variable name.
    """
    return var_name_list(stack, var)[0]


def register_assignment(stack, abstract_state, from_var ,to_var_name, split_stack=False):
    """
    Registers an assignment from one variable (or const value) to another to a given AbstractState.
    :param abstract_state: AbstractState to register assignment to.
    :param from_var: AST node to extract type and data from.
    :param to_var_name: variable name to assign data to.
    """
    actual_to_name = stack_var_name(stack, to_var_name)
    if split_stack:
        updated_stack = stack[0:-1]
    else:
        updated_stack = stack
    # TODO the node can be const
    if type(from_var) is ast.Name or type(from_var) is ast.Attribute:
        actual_from_name = actual_var_name(updated_stack, abstract_state, from_var.id)
        abstract_state.set_var_to_var(actual_to_name, actual_from_name)
    else:
        abstract_state.set_var_to_const(actual_to_name, getattr(from_var, from_var._fields[0]))

def evaluate_function(function, args, keywords, stack, abstract_state, functions):
    stack.append(function.name)
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
            register_assignment(stack, abstract_state, default, keyword.arg, True)
    assess_list(function.body, stack, abstract_state, functions)
    stack.pop()


class CallVisitor(ast.NodeVisitor):

    def __init__(self, stack, abstract_state, functions):
        super(CallVisitor, self).__init__()
        self.abstract_state = abstract_state
        self.functions = functions
        self.stack = stack

    def visit_Call(self, node):
        if node.func.id not in self.functions:
            raise Exception('Class or function not found %s' % (node.func.id))  # Maybe should be top?
        evaluate_function(self.functions[node.func.id], node.args, node.keywords, self.stack, self.abstract_state, self.functions)


class AssignVisitor(CallVisitor):

    def __init__(self, name, stack, abstract_state, functions):
        """
        Handle assign calls. Adds to the object the relavent methods and attributes
        """
        super(AssignVisitor, self).__init__(stack, abstract_state, functions)
        self.name = name
        self.abstract_state = abstract_state
        self.functions = functions
        self.stack = stack

    def visit_Attribute(self, node):
        """
        Handles attribute node.
        :param node: Attribute Node.
        """
        # TODO: it may be set_var_to_const
        self.abstract_state.set_var_to_var(self.name, get_node_name(node))

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
        register_assignment(self.stack, self.abstract_state, node, self.name)

    def visit_Tuple(self, node):
        """
        Handles tuple node.
        :param node: Tuple Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)

    def visit_Dict(self, node):
        """
        Handles dictionary node.
        :param node: Dictionary Node.
        """
        register_assignment(self.stack, self.abstract_state, node, self.name)


class ExprVisitor(CallVisitor):

    def __init__(self, stack, abstract_state, functions):
        super(ExprVisitor, self).__init__(stack, abstract_state, functions)


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def visit_FunctionDef(self, node):
        self.context[node.name] = node


def initialize_abstract_state(abstract_state):
    # TODO - it should be in Avial's code
    abstract_state.set_var_to_const('True', True)
    abstract_state.set_var_to_const('False', False)
    abstract_state.set_var_to_const('None', None)


class ProgramVisitor(ast.NodeVisitor):

    def __init__(self, stack=[], abstract_state=None, functions={}):
        """
        Should visit all the program
        """
        super(ProgramVisitor, self).__init__()
        if abstract_state is None:
            self.abstract_state = AbstractState()
            initialize_abstract_state(self.abstract_state)
        else:
            self.abstract_state = abstract_state
        self.stack = stack
        self.functions = functions

    def visit_ClassDef(self, node):
        """
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)
        ClassDefVisitor().visit(node)
        """
        raise Exception('Call visit is not supported yet')

    def visit_FunctionDef(self, node):
        FunctionDefVisitor(self.functions).visit(node)

    def visit_Expr(self, node):
        ExprVisitor(self.stack, self.abstract_state, self.functions).visit(node)

    def visit_Assign(self, node):
        """
        Handles assignment to variable.
        :param node: Current assignment node.
        """
        handle_assign(node, self.stack, self.abstract_state, self.functions)

    def visit_If(self, node):
        """
        Handles if/elif/else cases by assessing every option and than calculating the Least Upper Bound for them all.
        :param node: Current if node.
        """
        if len(node.orelse) == 0:
            before_if_states = self.abstract_state.clone()
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            self.abstract_state.lub(before_if_states)
        else:
            orelse_state = self.abstract_state.clone()
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            assess_list(node.orelse, self.stack, orelse_state, self.functions)
            self.abstract_state.lub(orelse_state)

    def visit_TryFinally(self, node):
        assess_list(node.body, self.abstract_state, self.functions, self.functions)
        assess_list(node.finalbody, self.abstract_state, self.functions, self.functions)

    def visit_TryExcept(self, node):
        before_block_abstract_states = self.abstract_state.clone()

        # If no exception raises
        try_block = node.body
        try_block_abstract_states = before_block_abstract_states.clone()
        assess_list(try_block, try_block_abstract_states, self.functions)
        self.abstract_state.lub(try_block_abstract_states, self.functions)

        # If exception raises during the execution
        helper = []
        for expr in try_block:
            helper.append(expr)
            current_abstract_states = before_block_abstract_states.clone()
            assess_list(helper, current_abstract_states)

            for handler in node.handlers:
                # TODO should add scope var with the "as e"
                handler_abstract_states = current_abstract_states.clone()
                assess_list(handler.body, handler_abstract_states)
                self.abstract_state.lub(handler_abstract_states)


def assess_list(entries, stack, abstract_state, functions):
    """
    Generates a ProgramVisitor and runs it through the given set of entries while updating the given AbstractState.
    :param entries: A list of entries to process.
    :param abstract_state: AbstractState to initialize the ProgramVisitor with.
    """
    visitor = ProgramVisitor(stack, abstract_state, functions)
    for entry in entries:
        visitor.visit(entry)


def handle_assign(node, stack, abstract_state, functions):
    """
    Handles assign - creates the relevant object and connects it to the context.
    """
    if len(node.targets) is not 1:
        # The simpler simples it
        raise Exception('Multiple targets does not supported (%s)' % node.name)

    assign_visitor = AssignVisitor(get_node_name(node.targets[0]), stack, abstract_state, functions)
    assign_visitor.visit(node.value)
