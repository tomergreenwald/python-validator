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
        #we do not handle multiple targets since we assume that the ast was preprocessed and every multiple assignment
        #was split into separate assignments with temporary variables.
        node_targets = node.targets[0]
        if hasattr(node_targets, 'value'):
            target = node_targets.value.id
            attr = node_targets.attr
            value = AttributeVisitor(self.class_dict).visit(node.value)
            if target is 'self':
                self.current_class.attributes[attr] = value
                #TODO: register assignment to 'self' with Aviel's data structure
            else:
                pass
                #TODO: register assignment to 'target' with Aviel's data structure. in this case the assignment is to a
                #paramater sent to the __init__ method
        else:
            #target = global variables
            attr = node_targets.id
            value = AttributeVisitor(self.class_dict).visit(node.value)
            i = 1
            #TODO: register assignment to 'global' with Aviel's data structure.