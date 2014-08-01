class MethodRepresentation(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.arguments = []

    def __repr__(self):
        return '<Method %s, arguments: %s>' % (self.name, self.arguments)
