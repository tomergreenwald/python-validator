from ast import NodeVisitor
from util import ClassRepresentation
from validator.visitors.ClassVisitor import ClassVisitor


class ProgramVisitor(NodeVisitor):
    def __init__(self, class_dict):
        """
        Class constructor.
        :param class_dict: Dictionary between class names and their ClassRepresentation.
        """
        self.class_dict = class_dict

    def visit_ClassDef(self, node):
        """
        Visitor function used by the NodeVisitor as a callback function which
        is called for every ClassDef instance it encounters.
        :param node: ClassDef node to handle.
        :raise Exception: If the current ClassDef was already declared (and
        parsed) or has multiple inheritance an exception will be thrown.
        """
        if node.name in self.class_dict:
            raise Exception('Multiple definitions per class are not supported (%s)' % node.name)
        if len(node.bases) is not 1:
            raise Exception('Multiple inheritance is not supported (%s)' % node.name)

        clazz = ClassRepresentation(node.name)
        visitor = ClassVisitor(clazz, self.class_dict[node.bases[0].id], self.class_dict)
        visitor.visit(node)
        self.class_dict[node.name] = clazz