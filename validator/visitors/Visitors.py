import ast
import logging

from validator.state.abstract import AbstractState
from validator.state.utils import TOP_MAGIC_NAME, BasicMutableClass
from validator.representation.ClassRepresentation import ClassRepresentation
from validator.util import pretty_var_path

from tabulate import tabulate

table = []

class Frame(object):
    def __init__(self, frame_name):
        self.frame_name = frame_name
        self.variables = []

    def register(self, variable):
        self.variables.append(variable)

    def clear(self, abstract_state):
        for variable in sorted(self.variables)[::-1]:
            # abstract_state.remove_var(self.frame_name + "#" + variable)
            abstract_state.remove_var(self.frame_name + "#" + variable, False) # False means ignore non existent variables
            table.append([id(abstract_state),"Removed", None, pretty_var_path(self.frame_name + "#" + variable), []])


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
        # return get_node_name(node.value) + '#' + node.attr
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
    if var.startswith(TOP_MAGIC_NAME):
        return var
        
    frame_name = None
    if var in stack.frames[-(level + 1)].variables:
        frame_name = stack.frames[-(level + 1)].frame_name
    if var in stack.frames[0].variables:
        frame_name = stack.frames[0].frame_name

    if frame_name:
        if frame_name.startswith("__init__"):
            frame_name = frame_name.replace("__init__", "root")
        return frame_name + "#" + var
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
        make_top = False
        if from_var.id is "ret_val":
            actual_from_name = "ret_val"
        elif from_var.id.startswith(TOP_MAGIC_NAME):
            make_top = True
        else:
            if type(from_var) is ast.Attribute:
                actual_from_name = from_var.id
            else:
                actual_from_name = actual_var_name(stack, from_var.id, level)
        if make_top is False:
            errors = abstract_state.set_var_to_var(actual_to_name, actual_from_name)
            logging.info("assigned {from_var} to {to_var}".format(from_var=pretty_var_path(actual_from_name), to_var=pretty_var_path(actual_to_name)))
            logging.info('errors - ' + str(errors))
            table.append([id(abstract_state),"Assigned", pretty_var_path(actual_from_name), pretty_var_path(actual_to_name), str(errors)])
        else:
            errors = abstract_state.add_var_and_set_to_top(actual_to_name)
            logging.info("set var {to_var} to TOP".format(to_var=pretty_var_path(actual_to_name)))
            table.append([id(abstract_state),"Assigned", "TOP", pretty_var_path(actual_to_name), str(errors)])
            logging.info('errors - ' + str(errors))
    elif from_var is not None:
        if type(from_var) is ast.Tuple:
            errors = abstract_state.set_var_to_const(actual_to_name, tuple())
            logging.info("assigned {var_type} to {to_var}".format(var_type=tuple(),
                                                           to_var=pretty_var_path(actual_to_name)))
            logging.info('errors - ' + str(errors))
            table.append([id(abstract_state),"Assigned", "Tuple", pretty_var_path(actual_to_name), str(errors)])
        elif type(from_var) is ast.Dict:
            errors = abstract_state.set_var_to_const(actual_to_name, dict())
            logging.info("assigned {var_type} to {to_var}".format(var_type=dict(),
                                                           to_var=pretty_var_path(actual_to_name)))
            logging.info('errors - ' + str(errors))
            table.append([id(abstract_state),"Assigned", "DICT", pretty_var_path(actual_to_name), str(errors)])
        else:
            errors = abstract_state.set_var_to_const(actual_to_name, getattr(from_var, from_var._fields[0]))
            logging.info("assigned {var_type} to {to_var}".format(var_type=type(getattr(from_var, from_var._fields[0])),
                                                           to_var=pretty_var_path(actual_to_name)))
            logging.info('errors - ' + str(errors))
            table.append([id(abstract_state),"Assigned", type(getattr(from_var, from_var._fields[0])), pretty_var_path(actual_to_name), str(errors)])
    else:
        errors = abstract_state.set_var_to_const(actual_to_name, new_object)
        logging.info("assigned {var_type} to {to_var}".format(var_type=type(new_object), to_var=pretty_var_path(actual_to_name)))
        logging.info('errors - ' + str(errors))
        table.append([id(abstract_state),"Assigned", type(new_object), pretty_var_path(actual_to_name), str(errors)])


def handle_kwargs(abstract_state, args, function, keywords, stack):
    arguments = []
    for i in xrange(len(args)):
        # TODO what if len(args) != len(function.args.args) ? this means that there is wrong number of arguments! report it!
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
        elif type(node.func) is ast.Attribute and node.func.attr is '__init__':     # Super Call!
            evaluate_function(self.classes[node.func.value.args[0].id].base.methods['__init__'],
                              [ast.Name(id='self', ctx=ast.Store())] + node.args, node.keywords, self.stack,
                              self.abstract_state, self.functions)
        elif type(node.func) is ast.Attribute:
            function_name = node.func.attr
            _self = node.func.value.id
            if function_name is 'append':
                """
                This is append support. It assumes that _self is list.
                if there is not _self_vars_lub it means that this is the first element added to the list,
                so it register it. Else, it lub the new element.
                """

                if _self + '_vars_lub' in self.stack.current_frame().variables:
                    errors = self.abstract_state.query(actual_var_name(self.stack, _self + '_vars_lub'), False)
                    table.append([id(self.abstract_state),"Query", None, pretty_var_path(actual_var_name(self.stack, _self + '_vars_lub')), errors])
                    if len(errors) == 0:
                        clone = self.abstract_state.clone()
                        table.append([id(self.abstract_state),"Clone state", None, id(clone), []])
                        clone.remove_var(actual_var_name(self.stack, _self + '_vars_lub'))
                        register_assignment(self.stack, clone, node.args[0], _self + '_vars_lub')
                        self.abstract_state.lub(clone)
                        table.append([id(self.abstract_state),"Lub states", None, id(clone), []])
                        logging.debug('LUB for %s_vars_lub' % _self)
                else:
                    register_assignment(self.stack, self.abstract_state, node.args[0], _self + '_vars_lub')
                    logging.debug(_self + '_vars_lub has created with %s' % node.args[0])
            else:
                #should return a list of contexts saved for each method (one per method impl)
                (methods, errors) = self.abstract_state.get_method_metadata(actual_var_name(self.stack, _self), function_name)
                table.append([id(self.abstract_state),"Retrieved method", function_name, pretty_var_path(actual_var_name(self.stack, _self)), str(errors)])
                logging.debug('possible methods are %s' %' '.join([x.name for x in methods]))
                # self.abstract_state.add_var_and_set_to_botom('ret_val')
                if errors:
                    logging.debug('Validation {level} in method {method}'.format(level=errors[0][0], method=errors[0][1]))

                # FIXME: why do we clone and never lub back abstract_state_clean?
                abstract_state_clean = self.abstract_state.clone()
                table.append([id(self.abstract_state),"Clone state", None, id(abstract_state_clean), []])
                cumulative_lub = None
                for method in methods:
                    abstract_state_cpy = abstract_state_clean.clone()
                    table.append([id(abstract_state_clean),"Clone state", None, id(abstract_state_cpy), []])
                    evaluate_function(method, [ast.Name(id=_self, ctx=ast.Load())] + node.args, node.keywords,
                                      self.stack,
                                      abstract_state_cpy,
                                      self.functions)
                    errors = abstract_state_cpy.query('ret_val', False)
                    table.append([id(abstract_state_cpy),"Query", None, 'ret_val', str(errors)])
                    if len(errors) > 0:
                        # copy doesnt contain ret_val
                        self.abstract_state.remove_var('ret_val', False)
                        table.append([id(self.abstract_state),"Removed", None, "ret_val", []])

                    if cumulative_lub is None:
                        cumulative_lub = abstract_state_cpy
                    else:
                        cumulative_lub.lub(abstract_state_cpy)

                    # self.abstract_state.lub(abstract_state_cpy)

                if cumulative_lub is not None:
                    self.abstract_state.set_to_state(cumulative_lub)
                    table.append([id(self.abstract_state),"Set to state", None, id(cumulative_lub), []])
        else:
            raise Exception("not supported")
        
        errors = self.abstract_state.query("ret_val", False)
        table.append([id(self.abstract_state),"Query", None, "ret_val", errors])
        if self.name and len(errors) == 0:
            register_assignment(self.stack, self.abstract_state, ast.Name(id="ret_val"), self.name)
            #self.abstract_state.set_var_to_var(actual_var_name(self.stack, self.name), "ret_val")
            self.abstract_state.remove_var("ret_val", False)
            table.append([id(self.abstract_state),"Removed", None, "ret_val", []])
        

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
        # name = actual_var_name(self.stack, node.value.id) + "#" + node.attr
        name = actual_var_name(self.stack, node.value.id) + "." + node.attr
        temp_node = ast.Attribute(id=name, ctx=ast.Store())
        register_assignment(self.stack, self.abstract_state, temp_node, self.name)

    def visit_Subscript(self, node):
        if type(node.ctx) is ast.Load:
            errors = self.abstract_state.query(actual_var_name(self.stack, node.value.id), False)
            table.append([id(self.abstract_state),"Query", None, pretty_var_path(actual_var_name(self.stack, node.value.id)), errors])
            if len(errors) > 0:
                raise Exception('List %s does not exists' % node.value.id)
            errors = self.abstract_state.query(actual_var_name(self.stack, node.value.id + '_vars_lub'), False)
            table.append([id(self.abstract_state),"Query", None, pretty_var_path(actual_var_name(self.stack, node.value.id + '_vars_lub')), errors])
            if len(errors) > 0:
                raise Exception('Try to load value from empty list %s' % node.value.id)

            self.visit_Name(ast.Name(id=node.value.id + '_vars_lub', ctx=ast.Load()))

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
        register_assignment(self.stack, self.abstract_state, node, self.name)  # Register the name as list

        list_lub = self.name + '_vars_lub'

        abstract_before = self.abstract_state.clone()
        table.append([id(self.abstract_state),"Clone state", None, id(abstract_before), []])
        if node.elts:
            register_assignment(self.stack, self.abstract_state, node.elts[0], list_lub)
        for item in node.elts[1:]:
            clone = abstract_before.clone()
            register_assignment(self.stack, clone, item, list_lub)
            self.abstract_state.lub(clone)
            table.append([id(self.abstract_state),"Lub state", None, id(clone), []])

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
            table.append([id(self.abstract_state),"Clone state", None, id(clone), []])
            register_assignment(self.stack, clone, item, tuple_lub)
            self.abstract_state.lub(clone)
            table.append([id(self.abstract_state),"Lub state", None, id(clone), []])

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
            table.append([id(self.abstract_state),"Clone state", None, id(clone), []])
            register_assignment(self.stack, clone, item, keys_lub)
            self.abstract_state.lub(clone)
            table.append([id(self.abstract_state),"Lub state", None, id(clone), []])

        values_lub = self.name + '_values_lub'
        if node.values:
            register_assignment(self.stack, self.abstract_state, node.values[0], values_lub)
        for item in node.values[1:]:
            clone = self.abstract_state.clone()
            table.append([id(self.abstract_state),"Clone state", None, id(clone), []])
            register_assignment(self.stack, clone, item, values_lub)
            self.abstract_state.lub(clone)
            table.append([id(self.abstract_state),"Lub state", None, id(clone), []])


class ExprVisitor(CallVisitor):
    def __init__(self, stack, abstract_state, functions, classes):
        super(ExprVisitor, self).__init__(stack, abstract_state, functions, classes)

    def visit_Attribute(self, node):
        name = actual_var_name(self.stack, node.value.id) + "." + node.attr
        logging.info("Evaluating expression - {name}".format(name=pretty_var_path(name)))
        errors = self.abstract_state.query(name)
        logging.info('errors - ' + str(errors))
        table.append([id(self.abstract_state),"Query", None, pretty_var_path(name), str(errors)])


class FunctionDefVisitor(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def visit_FunctionDef(self, node):
        self.context[node.name] = node


def initialize_abstract_state(abstract_state):
    errors = abstract_state.set_var_to_const('root#True', True)
    table.append([id(abstract_state),"Assigned", "True", "True", str(errors)])
    errors = abstract_state.set_var_to_const('root#False', False)
    table.append([id(abstract_state),"Assigned", "False", "False", str(errors)])
    errors = abstract_state.set_var_to_const('root#None', None)
    table.append([id(abstract_state),"Assigned", "None", "None", str(errors)])


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


class ProgramVisitor(ast.NodeVisitor):
    def __init__(self, stack=None, abstract_state=None, functions={}, classes={}):
        global table
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
        self.table = table

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
        logging.info('visit_For')
        register_assignment(self.stack, self.abstract_state, ast.Name(id=node.iter.id + '_vars_lub', ctx=ast.Load()), node.target.id)
        assess_list(node.body, self.stack, self.abstract_state, self.functions)

    def visit_If(self, node):
        """
        Handles if/elif/else cases by assessing every option and than calculating the Least Upper Bound for them all.
        :param node: Current if node.
        """
        if not node.orelse:
            before_if_states = self.abstract_state.clone()
            table.append([id(self.abstract_state),"Clone state", None, id(before_if_states), []])
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            self.abstract_state.lub(before_if_states)
            table.append([id(self.abstract_state),"Lub state", None, id(before_if_states), []])
        else:
            orelse_state = self.abstract_state.clone()
            table.append([id(self.abstract_state),"Clone state", None, id(orelse_state), []])
            assess_list(node.body, self.stack, self.abstract_state, self.functions)
            assess_list(node.orelse, self.stack, orelse_state, self.functions)
            # print 'queries'
            # print self.abstract_state.query('root#a.a.foo', False)
            # print orelse_state.query('root#a.a.foo', False)
            self.abstract_state.lub(orelse_state)
            table.append([id(self.abstract_state),"Lub state", None, id(orelse_state), []])

    def visit_TryFinally(self, node):
        if len(node.body) == 1 and type(node.body[0]) is ast.TryExcept:
            self.visit_TryExcept(node.body[0])
        else:
            before_block_abstract_state = self.abstract_state.clone()
            table.append([id(self.abstract_state),"Clone state", None, id(before_block_abstract_state), []])

            helper = []
            for expr in node.body:
                current_abstract_states = before_block_abstract_state.clone()
                table.append([id(before_block_abstract_state),"Clone state", None, id(current_abstract_states), []])
                helper.append(expr)
                assess_list(helper, self.stack, current_abstract_states, self.functions)
                self.abstract_state.lub(current_abstract_states)
                table.append([id(self.abstract_state),"Lub state", None, id(current_abstract_states), []])

        assess_list(node.finalbody, self.stack, self.abstract_state, self.functions)

    def visit_TryExcept(self, node):
        before_block_abstract_states = self.abstract_state.clone()
        table.append([id(self.abstract_state),"Clone state", None, id(before_block_abstract_states), []])

        # If no exception raises
        try_block = node.body
        assess_list(try_block, self.stack, self.abstract_state, self.functions)

        # If exception raises during the execution

        # Exception raises in the first expression.
        for handler in node.handlers:
            if handler.name:
                errors = self.abstract_state.set_var_to_const(handler.name.id, 'exception')
                table.append([id(self.abstract_state),"Assigned", handler.name.id, "exception", str(errors)])
            handler_abstract_states = before_block_abstract_states.clone()
            table.append([id(before_block_abstract_states),"Clone state", None, id(handler_abstract_states), []])
            assess_list(handler.body, self.stack, handler_abstract_states, self.functions)
            self.abstract_state.lub(handler_abstract_states)
            table.append([id(self.abstract_state),"Lub state", None, id(self.abstract_state), []])

        # Evaluate 1 expr or more
        helper = []
        for expr in try_block:
            helper.append(expr)
            current_abstract_states = before_block_abstract_states.clone()
            assess_list(helper, self.stack, current_abstract_states, self.functions)

            for handler in node.handlers:
                if handler.name:
                    errors = self.abstract_state.set_var_to_const(handler.name.id, 'exception')
                    table.append([id(self.abstract_state),"Assigned", handler.name.id, "exception", str(errors)])
                handler_abstract_states = current_abstract_states.clone()
                table.append([id(self.abstract_state),"Clone state", None, id(handler_abstract_states), []])
                assess_list(handler.body, self.stack, handler_abstract_states, self.functions)
                self.abstract_state.lub(handler_abstract_states)
                table.append([id(self.abstract_state),"Lub state", None, id(handler_abstract_states), []])

    def visit_Return(self, node):
        # if the statement is "return x" then to_name is "x"
        to_name = actual_var_name(self.stack, getattr(node.value, node.value._fields[0]))

        make_top = False
        if to_name.startswith(TOP_MAGIC_NAME):
            make_top = True

        logging.debug('visiting return. make top: %s' %make_top)
            
        errors = self.abstract_state.query('ret_val', False)
        table.append([id(self.abstract_state),"Query", None, 'ret_val', errors])
        if len(errors) == 0:
            temp_state = self.abstract_state.clone()
            table.append([id(self.abstract_state),"Clone state", None, id(temp_state), []])
            if make_top is False:
                errors = temp_state.set_var_to_var('ret_val', to_name)
                logging.info("assigned {from_var} to {to_var}".format(from_var=pretty_var_path(to_name), to_var="ret_val"))
                logging.info('errors - ' + str(errors))
                table.append([id(self.temp_state),"Assigned", pretty_var_path(to_name), "ret_val", str(errors)])
            else:
                temp_state.add_var_and_set_to_top('ret_val', force = True)
                logging.info("assigned {from_var} to {to_var}".format(from_var="TOP", to_var="ret_val"))
                table.append([id(temp_state),"Assigned", "TOP", "ret_val", []])
            self.abstract_state.lub(temp_state)
            table.append([id(self.abstract_state),"Lub state", None, id(temp_state), []])
        else:
            if make_top is False:
                errors = self.abstract_state.set_var_to_var('ret_val', to_name)
                logging.info("assigned {from_var} to {to_var}".format(from_var=pretty_var_path(to_name), to_var="ret_val"))
                logging.info('errors - ' + str(errors))
                table.append([id(self.abstract_state),"Assigned", pretty_var_path(to_name), "ret_val", str(errors)])
            else:
                self.abstract_state.add_var_and_set_to_top('ret_val', force = True)
                logging.info("assigned {from_var} to {to_var}".format(from_var="TOP", to_var="ret_val"))
                table.append([id(self.abstract_state),"Assigned", "TOP", "ret_val", []])


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

    if type(node.targets[0]) is ast.Subscript:
        try:
            actual_var_name(stack, node.targets[0].value.id)
            actual_var_name(stack, node.targets[0].value.id + '_vars_lub')
        except:
            raise Exception('Try to store value in uninitialized list')

        abstract_state_clone = abstract_state.clone()
        table.append([id(abstract_state),"Clone state", None, id(abstract_state_clone), []])

        assign_visitor = AssignVisitor(node.targets[0].value.id + '_vars_lub', stack, abstract_state, functions,
                                       classes)
        assign_visitor.visit(node.value)
        abstract_state.lub(abstract_state_clone)
        table.append([id(abstract_state),"Lub state", None, id(abstract_state_clone), []])
    else:
        assign_visitor = AssignVisitor(get_node_name(node.targets[0]), stack, abstract_state, functions, classes)
        assign_visitor.visit(node.value)


def init_object(target, abstract_state, clazz, args, keywords, stack, functions):
    """
    :param clazz: The ClassRepresentation of the class
    """
    
    logging.debug("Initializing object - %s", target)
    # we use BasicMutableClass becuase object() is primitive (can not add attributes to object())
    register_assignment(stack, abstract_state, None, target, new_object=BasicMutableClass())

    iter_clazz = clazz
    while iter_clazz is not 'object' and '__init__' not in iter_clazz.methods:
        iter_clazz = iter_clazz.base
    if iter_clazz is not 'object':
        evaluate_function(iter_clazz.methods['__init__'], [ast.Name(id=target, ctx=ast.Store())] + args, keywords,
                          stack, abstract_state, functions)

    iter_clazz = clazz
    while iter_clazz is not 'object':
        for method in iter_clazz.methods.values():
            logging.info("registering method - {method} to {var}".format(method=method.name, var=pretty_var_path(target)))
            errors = abstract_state.register_method_metadata(actual_var_name(stack, target), method.name, method)
            logging.info('errors - ' + str(errors))
            table.append([id(abstract_state),"Registered method", method.name, pretty_var_path(target), str(errors)])
        iter_clazz = iter_clazz.base
