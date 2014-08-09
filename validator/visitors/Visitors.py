import ast

from validator.state.abs_state import AbstractState


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


def register_assignment(abstract_state, from_var ,to_var_name):
    """
    Registers an assignment from one variable (or const value) to another to a given AbstractState.
    :param abstract_state: AbstractState to register assignment to.
    :param from_var: AST node to extract type and data from.
    :param to_var_name: variable name to assign data to.
    """
    # TODO the node can be const
    if type(from_var) is ast.Name or type(from_var) is ast.Attribute:
        abstract_state.set_var_to_var(to_var_name, from_var.id)
    else:
        abstract_state.set_var_to_const(to_var_name, getattr(from_var, from_var._fields[0]))


def evaluate_function(function, args, keywords, abstract_state):
    arguments = []
    for i in xrange(len(args)):
        arguments.append(i)
        register_assignment(abstract_state, args[i], function.args.args[i].id)
    for i in xrange(len(function.args.defaults)):
        arg_index = i + len(function.args.args) - len(function.args.defaults)
        arg = function.args.args[arg_index]
        found = False
        for keyword in keywords:
            if arg.id == keyword.arg:
                found = True
                register_assignment(abstract_state, keyword.value, keyword.arg)
        if not found:
            default = function.args.defaults[i]
            register_assignment(abstract_state, default, keyword.arg)
    assess_list(function.body, abstract_state)


class AssignVisitor(ast.NodeVisitor):
    """
    Handle assign calls. Adds to the object the relavent methods and attributes
    """

    def __init__(self, name, abstract_state, functions):
        super(AssignVisitor, self).__init__()
        self.name = name
        self.abstract_state = abstract_state
        self.functions = functions

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
        register_assignment(self.abstract_state, node, self.name)

    def visit_Num(self, node):
        """
        Handles number node.
        :param node: Number Node.
        """
        register_assignment(self.abstract_state, node, self.name)

    def visit_Name(self, node):
        """
        Handles name node (It means that we assign one variable to another - copy their pointers)..
        :param node: Name Node.
        """
        register_assignment(self.abstract_state, node, self.name)

    def visit_List(self, node):
        """
        Handles list node.
        :param node: List Node.
        """
        register_assignment(self.abstract_state, node, self.name)

    def visit_Tuple(self, node):
        """
        Handles tuple node.
        :param node: Tuple Node.
        """
        register_assignment(self.abstract_state, node, self.name)

    def visit_Dict(self, node):
        """
        Handles dictionary node.
        :param node: Dictionary Node.
        """
        register_assignment(self.abstract_state, node, self.name)

    def visit_Call(self, node):
        if node.func.id not in self.functions:
            raise Exception('Class or function not found %s' % (node.func.id))  # Maybe should be top?
        evaluate_function(self.functions[node.func.id], node.args, node.keywords, self.abstract_state)


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def visit_FunctionDef(self, node):
        self.context[node.name] = node


def initialize_abstract_state(abstract_state): # TODO - it should be in Avial's code
    abstract_state.set_var_to_const('True', True)
    abstract_state.set_var_to_const('False', False)
    abstract_state.set_var_to_const('None', None)


class ProgramVisitor(ast.NodeVisitor):
    """
    Should visit all the program
    """
    def __init__(self, abstract_state=None):
        super(ProgramVisitor, self).__init__()
        if abstract_state is None:
                self.abstract_state = AbstractState()
                initialize_abstract_state(self.abstract_state)
        else:
            self.abstract_state = abstract_state
        self.functions = {}

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
        raise Exception('Expr visit is not supported yet')

    def visit_Assign(self, node):
        """
        Handles assignment to variable.
        :param node: Current assignment node.
        """
        handle_assign(node, self.abstract_state, self.functions)

    def visit_If(self, node):
        """
        Handles if/elif/else cases by assessing every option and than calculating the Least Upper Bound for them all.
        :param node: Current if node.
        """
        if len(node.orelse) == 0:
            assess_list(node.body, self.abstract_state)
        else:
            orelse_state = self.abstract_state.clone()
            assess_list(node.body, self.abstract_state)
            assess_list(node.orelse, orelse_state)
            self.abstract_state.lub(orelse_state)


def assess_list(entries, abstract_state):
    """
    Generates a ProgramVisitor and runs it through the given set of entries while updating the given AbstractState.
    :param entries: A list of entries to process.
    :param abstract_state: AbstractState to initialize the ProgramVisitor with.
    """
    visitor = ProgramVisitor(abstract_state)
    for entry in entries:
        visitor.visit(entry)


def handle_assign(node, abstract_state, functions):
    """
    Handles assign - creates the relevant object and connects it to the context.
    """
    if len(node.targets) is not 1:
        # The simpler simples it
        raise Exception('Multiple targets does not supported (%s)' % node.name)

    assign_visitor = AssignVisitor(get_node_name(node.targets[0]), abstract_state, functions)
    assign_visitor.visit(node.value)