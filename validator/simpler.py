__author__ = 'Oded'

import ast
import _ast
from ast import *
import uuid

import codegen


should_simple_again = True


def random_tmp_var():
    return 'a' + str(uuid.uuid4()).replace('-', '')


def should_arth_simpler(node):
    return isinstance(node.value, _ast.BinOp) and (not isinstance(node.value.left, _ast.Name)
                                                   or not isinstance(node.value.right, _ast.Name))


def should_attr_simpler(node):
    return isinstance(node.value, _ast.Attribute) and (
    isinstance(node.value.value, _ast.Attribute) or isinstance(node.value.value, _ast.Call))


def should_call_simpler(node):
    return (isinstance(node.value, _ast.Call) and isinstance(node.value.func, _ast.Attribute)
            and (isinstance(node.value.func.value, _ast.Attribute) or isinstance(node.value.func.value, _ast.Call)))


def should_target_simpler(node):
    return isinstance(node, _ast.Assign) and not isinstance(node.targets[0], _ast.Name)


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
    new_node_left = None
    new_node_right = None
    if not isinstance(node.value.left, type(ast.Name())):
        tmp_var_name = random_tmp_var()
        new_node_left = ast.Assign(
            targets=[ast.Name(id=tmp_var_name, ctx=Store())],
            value=node.value.left
        )
        node.value.left = ast.Name(id=tmp_var_name, ctx=Load())
    elif not isinstance(node.value.right, type(ast.Name())):
        tmp_var_name = random_tmp_var()
        new_node_right = ast.Assign(
            targets=[ast.Name(id=tmp_var_name, ctx=Store())],
            value=node.value.right
        )
        node.value.right = ast.Name(id=tmp_var_name, ctx=Load())

    return new_node_left, new_node_right, node


def simple(node):
    global should_simple_again

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


def make_simple(code):
    """
    Gets a string represents the code and runs the simpler visitor.
    Return the code as a string after make it more "simple"
    """
    global should_simple_again

    ast_tree = ast.parse(code)
    while should_simple_again:
        should_simple_again = False
        visitor = CodeSimpler()
        visitor.visit(ast_tree)

    return codegen.to_source(ast_tree)