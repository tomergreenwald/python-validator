from ast import NodeVisitor
from validator.visitors.AttributeVisitor import AttributeVisitor
from validator.visitors.InitVisitor import InitVisitor


class ClassVisitor(NodeVisitor):
    def __init__(self, current_class, base_class, class_dict):
        self.current_class = current_class
        self.base_class = base_class
        self.class_dict = class_dict

    def visit_FunctionDef(self, node):
        if node.name is '__init__':
            for child_node in node.body:
                visitor = InitVisitor(self.current_class, self.base_class)
                visitor.visit(child_node)
        else:
            self.current_class.methods.append(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if node.targets[0].value.id is 'self':
            self.current_class.attributes[node.targets[0].attr]=AttributeVisitor(self.class_dict).visit(node.value)
        #FIXME: what do we do if the assignment is not to self?