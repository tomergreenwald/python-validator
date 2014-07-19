class LatticeElement(object):
    L_BOTOM = -1
    L_MAY_HAVE = 0
    L_MUST_HAVE = 1
    L_MUST_NOT_HAVE = 2
    TOTAL_ATTR_TYPES = 3
    
    def __init__(self, element):
        self.val = element
    
    def get_element_name(self):
        for v in dir(self):
            if v.startswith('L_') and self.__getattribute__(v) == self.val:
                return v
        return 'UNKNOWN_ELEMENT'
    
    def get_element_enum(self):
        """
        we want to associate each element with a number
        """
        return self.val
    
    @staticmethod
    def lub(p0, p1):
        """
        returns the lub of two primitive information
                            Top
                             |
                             |
                          MAY_HAVE
                           /    \
                          /      \
                         /        \
                        /          \
                   MUST_HAVE    MUST_NOT_HAVE
                       \            /
                        \          /
                         \        /
                          \      /
                           \    /
                           Bottom
        """
        if p0 == p1:
            return p0
        
        # This is the case for this lattice. if the lattice is changed, this function should be updated more carefully
        return LatticeElement.L_MAY_HAVE
        