class ClassRepresentation:
    def __init__(self, name):
        self.name = name
        self.methods = []
        self.attributes = {}

    def __repr__(self):
        return '<Class %s, methods: %s, attributes: %s>' % (self.name, self.methods, self.attributes)