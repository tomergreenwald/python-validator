from copy import copy


# lattice elements

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
        """
        self.attributes = dict()
        self._attributes_set = set()
        self.by_type = [set() for x in xrange(LatticeElement.TOTAL_ATTR_TYPES)] # TODO maybe we wont need this
    
    def add_attribute(self, new_attribute, attribute_sureance = None):
        """
        call this when you know something about a new_attribute
        new attribute should be a string
        """
        if attribute_sureance is None:
            attribute_sureance = LatticeElement(LatticeElement.L_MUST_HAVE)
        else:
            attribute_sureance = copy(attribute_sureance)
        self.attributes[new_attribute] = attribute_sureance
        self.by_type[attribute_sureance.get_element_enum()].add(new_attribute)
        self._attributes_set.add(new_attribute)
    
    def get_attribute_info(self, attribute):
        """
        call this when you want to know something about 'attribute'
        """
            
        # should we return MUST_NOT_HAVE instead of -1?
        return self.attributes.get(attribute, LatticeElement(LatticeElement.L_BOTOM))
    
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
            self.by_type[other_info.get_element_enum()].add(att)
        
        for att in common_attributes:
            self_info = self.attributes[att]
            other_info = other.attributes[att]
            new_info = LatticeElement.lub(self_info, other_info)
            if new_info != self_info:
                self.attributes[att] = new_info
                self.by_type[self_info.get_element_enum()].remove(att)
                self.by_type[new_info.get_element_enum()].add(att)
                updated = True
        
        return updated
    
    def __repr__(self):
        return '\n'.join(['%s: %s' %(x, y.get_element_name()) for (x,y) in self.attributes.items()])

    @staticmethod
    def generate_var_info(obj):
        """
        returns a new VariableInfo object with the information about the 
        attributes of obj. for example, if we know that variable x is an 
        integer, then we can use generate_var_info(5) in order to get a 
        VariableInfo object for x
        
        TODO write a function that wraps this function, and generates var 
             info up to some depth (using __getattribute__ function)
        """
        res = VariableInfo()
        
        for att in dir(obj):
            res.add_attribute(att, LatticeElement(LatticeElement.L_MUST_HAVE))
                
        return res
        