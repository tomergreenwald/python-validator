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
    return isinstance(node.value, _ast.Attribute) and not isinstance(node.value.value, _ast.Name)


def should_call_simpler(node):
    return isinstance(node.value, _ast.Call) and isinstance(node.value.func, _ast.Attribute) \
        and (isinstance(node.value.func.value, _ast.Attribute) or (isinstance(node.value.func.value, _ast.Call) and node.value.func.value.func.id is not 'super'))


def should_call_args_simpler(node):
    if not isinstance(node.value, _ast.Call):
        return False
    for a in node.value.args:
        if not isinstance(a, _ast.Name):
            return True
    for k in node.value.keywords:
        if not isinstance(k.value, _ast.Name):
            return True
    return False


def should_target_simpler(node):
    return isinstance(node, _ast.Assign) and not (isinstance(node.targets[0], _ast.Name)
                                                  or (isinstance(node.targets[0], _ast.Attribute)
                                                      and isinstance(node.targets[0].value, _ast.Name))
                                                  or isinstance(node.targets[0], _ast.Subscript))


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
    for k in node.value.keywords:
        if not isinstance(k.value, _ast.Name):
            tmp_var_name = random_tmp_var()
            new_nodes.append(ast.Assign(
                targets=[ast.Name(id=tmp_var_name, ctx=Store())],
                value=k.value
            )
            )
            k.value = ast.Name(id=tmp_var_name, ctx=Load())
    return new_nodes + [node]


def assign_tuple_simpler(node):
    tmp_var_name = random_tmp_var()

    return_nodes = [ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=node.value)]
    for v, index in zip(node.targets[0].elts, xrange(len(node.targets[0].elts))):
        return_nodes.append(ast.Assign(targets=[ast.Name(id=v.id, ctx=Store())],
                                       value=Subscript(value=Name(id=tmp_var_name, ctx=Load()),
                                                       slice=Index(value=Num(n=index))),
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
        value=node.targets[0].value
    )
    node.targets[0].value = ast.Name(id=tmp_var_name, ctx=Load())
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

    if type(node.value) in [ast.List, ast.Tuple]:
        list_extractor = []
        for i, v in enumerate(node.value.elts):
            if not isinstance(v, ast.Name):
                should_simple_again = True
                tmp_var_name = random_tmp_var()
                list_extractor.append(ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=v))
                node.value.elts[i] = ast.Name(id=tmp_var_name, ctx=Load())
        return list_extractor + [node]

    if type(node.value) is ast.Dict:
        dict_extractor = []
        for i, k in enumerate(node.value.keys):
            v = node.value.values[i]
            if not isinstance(k, ast.Name):
                should_simple_again = True
                tmp_var_name = random_tmp_var()
                dict_extractor.append(ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=k))
                node.value.keys[i] = ast.Name(id=tmp_var_name, ctx=Load())
            if not isinstance(v, ast.Name):
                should_simple_again = True
                tmp_var_name = random_tmp_var()
                dict_extractor.append(ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=v))
                node.value.values[i] = ast.Name(id=tmp_var_name, ctx=Load())
        return dict_extractor + [node]

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

    def visit_For(self, node):
        if not isinstance(node.iter, ast.Name):
            global should_simple_again
            should_simple_again = True

            tmp_var_name = random_tmp_var()
            list_assign_node = ast.Assign(
                targets=[ast.Name(id=tmp_var_name, ctx=Store())],
                value=node.iter
            )
            node.iter = ast.Name(id=tmp_var_name, ctx=Load())
            return list_assign_node, node
        return self.generic_visit(node)

    def visit_Return(self, node):
        if type(node.value) is not ast.Name:
            global should_simple_again
            should_simple_again = True

            tmp_var_name = random_tmp_var()
            return [
                ast.Assign(targets=[ast.Name(id=tmp_var_name, ctx=Store())], value=node.value),
                ast.Return(value=ast.Name(id=tmp_var_name, ctx=Load()))
            ]
        return node

    def visit_Dict(self, node):
        raise Exception('Dictionary is not supported')


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