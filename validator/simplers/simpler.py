__author__ = 'Oded'

import ast
import _ast
from ast import *
import uuid

import astor


should_simple_again = None


def random_tmp_var():
    return 'a' + str(uuid.uuid4()).replace('-', '')


def should_assign_tuple_simpler(node):
    return isinstance(node, _ast.Assign) and isinstance(node.targets[0], _ast.Tuple)


def should_arth_simpler(node):
    return isinstance(node.value, _ast.BinOp) and (not isinstance(node.value.left, _ast.Name)
                                                   or not isinstance(node.value.right, _ast.Name))


def should_attr_simpler(node):
    return isinstance(node.value, _ast.Attribute) and (
    isinstance(node.value.value, _ast.Attribute) or isinstance(node.value.value, _ast.Call))


def should_call_simpler(node):
    return (isinstance(node.value, _ast.Call) and isinstance(node.value.func, _ast.Attribute)
            and (isinstance(node.value.func.value, _ast.Attribute) or isinstance(node.value.func.value, _ast.Call)))


def should_call_args_simpler(node):
    if not isinstance(node.value, _ast.Call):
        return False
    for a in node.value.args:
        if not isinstance(a, _ast.Name):
            return True
    return False


def should_target_simpler(node):
    return isinstance(node, _ast.Assign) and not isinstance(node.targets[0], _ast.Name)


def call_args_simpler(node):
    new_nodes = []
    for a, index in zip(node.value.args, xrange(len(node.value.args))):
        if not isinstance(a, _ast.Name):
            tmp_var_name = random_tmp_var()
            new_nodes.append(ast.Assign(
                                        targets=[ast.Name(id=tmp_var_name, ctx=Store())],
                                        value=a
                                        ))
            node.value.args[index] = ast.Name(id=tmp_var_name, ctx=Load())
    return new_nodes + [node]


def assign_tuple_simpler(node):
    tmp_var_name = random_tmp_var()

    return_nodes = [ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=node.value)]
    for v, index in zip(node.targets[0].elts, xrange(len(node.targets[0].elts))):
        return_nodes.append(ast.Assign(targets=[ast.Name(id=v.id, ctx=Store())],
                                       value=Subscript(value=Name(id=tmp_var_name, ctx=Load()), slice=Index(value=Num(n=index))),
                                       ctx=Load()
                                       ))
    return return_nodes


def call_simpler(node):
    tmp_var_name = random_tmp_var()
    new_node = ast.Assign(
        targets=[ast.Name(id=tmp_var_name, ctx=Store())],
        value=node.value.func.value
    )
    node.value.func.value = ast.Name(id=tmp_var_name, ctx=Load())
    return new_node, node


def targets_simpler(node):
    tmp_var_name = random_tmp_var()
    new_node = ast.Assign(
        targets=[ast.Name(id=tmp_var_name, ctx=Store())],
        value=node.targets[0]
    )
    node.targets[0] = ast.Name(id=tmp_var_name, ctx=Store())
    return new_node, node


def attr_simpler(node):
    tmp_var_name = random_tmp_var()
    new_node = ast.Assign(
        targets=[ast.Name(id=tmp_var_name, ctx=Store())],
        value=node.value.value
    )
    node.value.value = ast.Name(id=tmp_var_name, ctx=Load())
    return new_node, node


def arth_simpler(node):
    returned_body = []

    if not isinstance(node.value.left, type(ast.Name())):
        tmp_var_name = random_tmp_var()
        new_node_left = ast.Assign(
            targets=[ast.Name(id=tmp_var_name, ctx=Store())],
            value=node.value.left
        )
        node.value.left = ast.Name(id=tmp_var_name, ctx=Load())
        returned_body.append(new_node_left)
    if not isinstance(node.value.right, type(ast.Name())):
        tmp_var_name = random_tmp_var()
        new_node_right = ast.Assign(
            targets=[ast.Name(id=tmp_var_name, ctx=Store())],
            value=node.value.right
        )
        node.value.right = ast.Name(id=tmp_var_name, ctx=Load())
        returned_body.append(new_node_right)
    returned_body.append(node)

    return returned_body


def simple(node):
    global should_simple_again

    if should_assign_tuple_simpler(node):
        should_simple_again = True
        return assign_tuple_simpler(node)

    if should_target_simpler(node):
        should_simple_again = True
        return targets_simpler(node)

    if should_attr_simpler(node):
        should_simple_again = True
        return attr_simpler(node)

    if should_call_simpler(node):
        should_simple_again = True
        return call_simpler(node)

    if should_arth_simpler(node):
        should_simple_again = True
        return arth_simpler(node)

    if should_call_args_simpler(node):
        should_simple_again = True
        return call_args_simpler(node)

    return node


class CodeSimpler(ast.NodeTransformer):
    def visit_Assign(self, node):
        return simple(node)

    def visit_Expr(self, node):
        return simple(node)

    def visit_AugAssign(self, node):
        global should_simple_again
        should_simple_again = True

        return ast.Assign(
            targets=[node.target],
            value=ast.BinOp(left=node.target, op=node.op, right=node.value)
        )


class BinOpHelper(ast.NodeVisitor):
    def visit_Add(self, node):
        return '__add__'

    def visit_Mult(self, node):
        return '__mul__'

    def visit_Sub(self, node):
        return '__sub__'

    def visit_Div(self, node):
        return '__div__'


class BinOpTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        global should_simple_again
        should_simple_again = True
        return ast.Call(func=Attribute(value=node.left, attr=BinOpHelper().visit(node.op), ctx=Load()),
                        args=[node.right], keywords=[], starargs=None, kwargs=None)


def make_simple(code):
    """
    Gets a string represents the code and runs the simpler visitor.
    Return the code as a string after make it more "simple"
    """
    global should_simple_again
    should_simple_again = True

    ast_tree = ast.parse(code)
    while should_simple_again:
        should_simple_again = False
        visitor = CodeSimpler()
        visitor.visit(ast_tree)

    should_simple_again = True
    while should_simple_again:
        should_simple_again = False
        visitor = BinOpTransformer()
        visitor.visit(ast_tree)
    return astor.codegen.to_source(ast_tree)