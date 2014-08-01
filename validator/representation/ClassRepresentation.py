class ClassRepresentation(object):
    def __init__(self, name, base=None):
        self.name = name
        self.base = base
        self.methods = {}
        self.static_methods = {}
        self.static_vars = {}

    def __repr__(self):
        return '<Class %s, base: %s, methods: %s, static_methos: %s, static_vars: %s' % \
               (self.name, self.base, self.methods, self.static_methods, self.static_vars)
