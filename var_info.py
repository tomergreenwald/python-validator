# lattice elements
MAY_HAVE = 0
MUST_HAVE = 1
MUST_NOT_HAVE = 2
TOTAL_ATTR_TYPES = 3

STATES_INV = {0: 'MAY_HAVE', 1: 'MUST_HAVE', 2: 'MUST_NOT_HAVE'}

def lattice_lub(p0, p1):
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
    return MAY_HAVE

class VariableInfo(object):
    """
    This class represents everything we can know about attributes of an object
    currently it contains only a set of the attributes that the object CAN has
    in the future it can contain their types
    """
    def __init__(self):
        """
        we manage 4 members:
            _attributes_set: a set containing all attributes for this object (only for convenience)
            attributes: a dict from attribute name to an element in the lattice
            by_type: the inverse mapping of attributes
            is_top: True if we know nothing about this variable
        """
        self.attributes = dict()
        self._attributes_set = set()
        self.by_type = [set() for x in xrange(TOTAL_ATTR_TYPES)]
        self.is_top = True
    
    def add_attribute(self, new_attribute, attribute_sureance = MAY_HAVE):
        """
        call this when you know something about a new_attribute
        new attribute should be a string
        """
        self.is_top = False
        self.attributes[new_attribute] = attribute_sureance
        self.by_type[attribute_sureance].add(new_attribute)
        self._attributes_set.add(new_attribute)
    
    def get_attribute_info(self, attribute):
        """
        call this when you want to know something about 'attribute'
        """
        if self.is_top:
            return MAY_HAVE
            
        # should we return MUST_NOT_HAVE ?
        return self.attributes.get(attribute, -1)
    
    def set_top():
        """
        call this when you know nothing
        """
        self.attributes.clear()
        self._attributes_set.clear()
        for s in self.by_type:
            s.clear()
        self.is_top = True
    
    def lub_update(self, other):
        """
        perform the lub operator between self and other.
        modifies self to be the result
        return True if the result updated the object
        """
        updated = False
        # self_attributes = self._attributes_set.difference(other._attributes_set) # we dont really need to update these attributes...
        other_attributes = other._attributes_set.difference(self._attributes_set)
        common_attributes = self._attributes_set.intersection(other._attributes_set)
        
        if len(other_attributes):
            updated = True
        
        for att in other_attributes:
            other_info = other.attributes[att]
            self.attributes[att] = other_info
            self._attributes_set.add(att)
            self.by_type[other_info].add(att)
        
        for att in common_attributes:
            self_info = self.attributes[att]
            other_info = other.attributes[att]
            new_info = lattice_lub(self_info, other_info)
            if new_info != self_info:
                self.attributes[att] = new_info
                self.by_type[self_info].remove(att)
                self.by_type[new_info].add(att)
                updated = True
        
        return updated
    
    def __repr__(self):
        return '\n'.join(['%s: %s' %(x,STATES_INV[y]) for (x,y) in self.attributes.items()])
