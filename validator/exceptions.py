class MultipleNameDefinition(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Validator does not support multiple definitons with the same name (%s)' % self.name
        