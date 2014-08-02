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


class AssignVisitor(ast.NodeVisitor):
    """
    Handle assign calls. Adds to the object the relavent methods and attributes
    """

    def __init__(self, name, abstract_state):
        super(AssignVisitor, self).__init__()
        self.name = name
        self.abstract_state = abstract_state

    def visit_Attribute(self, node):
        """
        Handles attribute node.
        :param node: Attribute Node.
        """
        self.abstract_state.set_var_to_var(self.name, get_node_name(node))

    def visit_Str(self, node):
        """
        Handles string node.
        :param node: String Node.
        """
        self.abstract_state.set_var_to_const(self.name, node.s)

    def visit_Num(self, node):
        """
        Handles number node.
        :param node: Number Node.
        """
        self.abstract_state.set_var_to_const(self.name, node.n)

    def visit_Name(self, node):
        """
        Handles name node (It means that we assign one variable to another - copy their pointers)..
        :param node: Name Node.
        """
        self.abstract_state.set_var_to_var(self.name, node.id)

    def visit_List(self, node):
        """
        Handles list node.
        :param node: List Node.
        """
        self.abstract_state.set_var_to_const(self.name, node.elts)

    def visit_Tuple(self, node):
        """
        Handles tuple node.
        :param node: Tuple Node.
        """
        self.abstract_state.set_var_to_const(self.name, node.elts)

    def visit_Dict(self, node):
        """
        Handles dictionary node.
        :param node: Dictionary Node.
        """
        self.abstract_state.set_var_to_const(self.name, node)

    def visit_Call(self, node):
        """
        if node.func.id is 'set':
            self.obj.simple = 'set'

        #FIXME: we do not support call for regular functions (that are not constructors)
        if node.func.id not in classes and node.func.id not in functions:
            raise Exception('Class or function not found %s' % (node.func.id))  # Maybe should be top?
        init_object(self.obj, classes[node.func.id], node.args, node.keywords)
        # node.func.id can be in functions or something like that
        """
        raise Exception('Call visit is not supported yet')


def initialize_abstract_state(abstract_state):
    abstract_state.set_var_to_const('True', True)
    abstract_state.set_var_to_const('False', False)
    abstract_state.set_var_to_const('None', None)


class ProgramVisitor(ast.NodeVisitor):
    def __init__(self, abstract_state=None):
        if abstract_state is None:
            self.abstract_state = AbstractState()
            initialize_abstract_state(self.abstract_state)
        else:
            self.abstract_state = abstract_state

    """
    Should visit all the program
    """

    def visit_ClassDef(self, node):
        """
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance does not supported (%s)' % node.name)
        ClassDefVisitor().visit(node)
        """
        raise Exception('Call visit is not supported yet')

    def visit_FunctionDef(self, node):
        """
        FunctionDefVisitor().visit(node)
        """
        raise Exception('Call visit is not supported yet')

    def visit_Assign(self, node):
        """
        Handles assignment to variable.
        :param node: Current assignment node.
        """
        handle_assign(node, self.abstract_state)

    def visit_If(self, node):
        """
        Handles if/elif/else cases by assessing every option and than calculating the Least Upper Bound for them all.
        :param node: Current if node.
        """
        if len(node.orelse) == 0:
            self.asses_list(node.body, self.abstract_state)
        else:
            orelse_state = self.abstract_state.clone()
            self.asses_list(node.body, self.abstract_state)
            self.asses_list(node.orelse, orelse_state)
            self.abstract_state.lub(orelse_state)


    def asses_list(self, entries, abstract_state):
        """
        Generates a ProgramVisitor and runs it through the given set of entries while updating the given AbstractState.
        :param entries: A list of entries to process.
        :param abstract_state: AbstractState to initialize the ProgramVisitor with.
        """
        visitor = ProgramVisitor(abstract_state)
        for entry in entries:
            visitor.visit(entry)


def handle_assign(node, abstract_state):
    """
    Handles assign - creates the relavent object and connects it to the context.
    """
    if len(node.targets) is not 1:
        raise Exception('Multiple targets does not supported (%s)' % node.name)

    assign_visitor = AssignVisitor(get_node_name(node.targets[0]), abstract_state)
    assign_visitor.visit(node.value)

