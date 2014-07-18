from ast import NodeVisitor


class AttributeVisitor(NodeVisitor):
    def __init__(self, class_dict):
        """
        Class constructor.
        :param class_dict: Dictionary between class names and their ClassRepresentation.
        """
        self.class_dict = class_dict

    def visit_Str(self, node):
        return 'str'

    def visit_Num(self, node):
        return 'num'

    def visit_Name(self, node):
        if node.id is 'None':
            return 'NoneType'
        else:
            return 'bool'

    def visit_List(self, node):
        return 'list'

    def visit_Tuple(self, node):
        return 'tuple'

    def visit_Call(self, node):
        if node.func.id is 'set':
            raise Exception('Set is not supported')
        if node.func.id not in self.class_dict.keys():
            return
            #raise Exception()
            #FIXME: the call does not have to be to a class, it can be to a method too
            #FIXME: We do not identify calls to methods we haven't parsed yet
        return self.class_dict[node.func.id]