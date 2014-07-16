from ast import NodeVisitor
from util import inharite_methods_and_attributes


class InitVisitor(NodeVisitor):
    def __init__(self, current_class, base_class):
        self.current_class = current_class
        self.base_class = base_class

    def visit_Expr(self, node):
        try:
            if node.value.func.value.func.id is 'super':
                inharite_methods_and_attributes(self.current_class, self.base_class)
        except Exception as e:
            print e
        try:
            if node.value.func.value.id is self.base_class.name:
                inharite_methods_and_attributes(self.current_class, self.base_class)
        except Exception as e:
            print e
            #FIXME: we are shadowing an error here
            pass

    def visit_Assign(self, node):
        pass
        #TODO implement me