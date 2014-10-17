from state_exceptions import VerifierError, VerifierWarning


class LatticeElement(object):
    L_BOTOM = -1
    L_MAY_HAVE = 0
    L_MUST_HAVE = 1
    L_MUST_NOT_HAVE = 2
    L_TOP = 3
    TOTAL_ATTR_TYPES = 4

    def __init__(self, element):
        self.val = element

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_element_name(self):
        for v in dir(self):
            if v.startswith('L_') and self.__getattribute__(v) == self.val:
                return v
        return 'UNKNOWN_ELEMENT'

    def __repr__(self):
        return self.get_element_name()

    def get_element_enum(self):
        """
        we want to associate each element with a number
        """
        return self.val

    def is_legal(self):
        if self.val == LatticeElement.L_MAY_HAVE:
            raise VerifierWarning("Attribute might not exist")
        elif self.val == LatticeElement.L_MUST_NOT_HAVE or self.val == LatticeElement.L_BOTOM:
            raise VerifierError("Attribute does not exist")

    def inplace_lub(self, p):
        self.val = self.lub(self, p).val

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
            return LatticeElement(p0.val)

        if p0.val == LatticeElement.L_BOTOM:
            return LatticeElement(p1.val)
        if p1.val == LatticeElement.L_BOTOM:
            return LatticeElement(p0.val)

        if p0.val == LatticeElement.L_TOP or p1.val == LatticeElement.L_TOP:
            return LatticeElement(LatticeElement.L_TOP)

        if p0.val == LatticeElement.L_MAY_HAVE or p1.val == LatticeElement.L_MAY_HAVE:
            return LatticeElement(LatticeElement.L_MAY_HAVE)

        # This is the case for this lattice. if the lattice is changed, this function should be updated more carefully
        return LatticeElement(LatticeElement.L_MAY_HAVE)
