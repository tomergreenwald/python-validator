from collections import deque
from copy import copy, deepcopy
import logging
# logging.basicConfig(level = logging.DEBUG)

from var_info import VariableInfo
from exceptions import VarNotInState

    
class AbstractState(object):
    """
    This class represents the abstract state for a set of variables (which means the abstract state for the whole program)
    it contains information about the graph of the program
    useful interface functions:
        output:
            check_attr
            has_var
            clone
        input:
            set_var_to_const
            set_var_to_var
            add_var_attribute
            forget_var
            lub
    """
    def __init__(self):
        """
        we have the following members:
            vars_info: a mapping between each variable to an VariableInfo 
                       object
            vars_set: a set of all variables in vars_info, only for convenience
            seeded_by: for every variable, a set of the variables it can be 
                       seeded from (e.g. if x=y, then x is seeded by y)
            seeds: for every variable, a set of variables which is seeds 
                   (e.g. if x=y, then y seeds x. if y=z, then y stops to seed x)
            need_to_update: nodes that needs to propagate their info to their 
                            sons in the graph. actually, all the objects that
                            their ref-count is more than 1
        """
        self.vars_info = dict()
        self.vars_set = set()
        self.seeded_by = dict()
        self.seeds = dict()
        self.need_to_update = set()
        
    def clone(self):
        """
        return a copy of the abstract state
        """
        return deepcopy(self)
    
    def query(self, var, attr):
        if var not in self.vars_set:
            raise VarNotInState('Querying a variable not in the state')
        self._flush_all_seeds()
        return self.vars_info[var].get_attribute_info(attr)
    
    def check_attr(self, var, attr):
        """
        call this when you want to know if attribute attr of variable var
        is valid. might raise:
            VarNotInState   - when var doesnt exist
            VerifierError   - when attribute doesnt exist
            VerifierWarning - when attribute might not exist
        """
        self.query(var, attr).is_legal()
    
    def set_var(self, var, var_info):
        """
        call this when you know some VariableInfo about var
        """
        if var in self.vars_set:
            self._clear_seeds(var)
        else:        
            self.vars_set.add(var)
            self.seeds[var] = set()
            self.seeded_by[var] = set()
        
        # TODO do we really need to copy var_info?
        self.vars_info[var] = deepcopy(var_info)
        self.need_to_update.add(var)
    
    def _clear_seeds(self, v):
        """
        propagate the knowledge we have on v towards its son
        """
        self._flush_all_seeds()
        
        for u in self.seeds[v]:
            self.seeded_by[u].remove(v)
        self.seeds[v].clear()
        
        for u in self.seeded_by[v]:
            self.seeds[u].remove(v)
        self.seeded_by[v].clear()
    
    def _flush_all_seeds(self):
        """
        flush everything we know along the tree
        this function must be called before any query is made
        """
        logging.debug('_flush_all_seeds')
        for v in self.need_to_update:
            logging.debug('flushing seeds from %s' %v)
            self._flush_seeds(v)
        
        self.need_to_update.clear()
    
    def _add_dependency(self, var0, var1):
        """
        var0 and var1 are the exact same instance of an object
        """
        self.seeds[var1].add(var0)
        self.seeded_by[var0].add(var1)
    
    def has_var(self, var):
        return var in self.vars_set
    
    def set_var_to_var(self, var0, var1):
        """
        call this when there is a statement var0 = var1, and var1 is a pointer (not a simple type such as integer)
        """
        logging.debug('set var %s to %s' %(var0, var1))
        if var1 not in self.vars_set:
            raise VarNotInState('Assignment not allowed (%s = %s) since %s is not set' % (var0, var1, var1))
            
        if var0 not in self.vars_set:
            self.vars_set.add(var0)
            self.seeds[var0] = set()
            self.seeded_by[var0] = set()
        
            
        self._clear_seeds(var0) # this also calls _flush_all_seeds
        
        self._add_dependency(var0, var1)
        self._add_dependency(var1, var0)
        
        self.need_to_update.add(var1)
        self.need_to_update.add(var0)
        
        self.vars_info[var0] = VariableInfo()
        
    def set_var_to_const(self, var0, val0):
        """
        call this function when a by-value assignment is done, such as x = 5
        we base this function on dir(val0), so we expect val0 to consist of a 
        known type during analysis time
        """
        logging.debug('set var %s to const' %var0)
        
        vi = VariableInfo.generate_var_info(val0)
        if var0 not in self.vars_set:
            self.set_var(var0, vi)
        else:
            self._clear_seeds(var0) # this also calls _flush_all_seeds
            self.vars_info[var0] = vi
        
        self.need_to_update.add(var0)
    
    def add_var_attribute(self, var, attr, attr_surance = None):
        """
        call this function when attribute "attr" of variable "var" is set.
        whenever a line like this is executed:
            var.attr = 5
        """
        logging.debug('adding attribute %s to var %s' %(attr, var))
        if var in self.vars_set:
            self.vars_info[var].add_attribute(attr, attr_surance)
        else:
            raise VarNotInState('Setting Value to a variable not in the state')
        
        self.need_to_update.add(var)
    
    def forget_var(self, var):
        """
        call this when a var is get out of scope (or if it is a temporary var)
        """
        self._flush_all_seeds()
        
        del self.vars_info[var]
        self.vars_set.remove(var)
        
        for s in self.seeds[var]:
            self.seeded_by[s].remove(var)
        del self.seeds[var]
        
        for s in self.seeded_by[var]:
            self.seeds[s].remove(var)
        del self.seeded_by[var]
    
    def lub(self, other):
        """
        we take the union of both graphes (seeded_by)
        modified self:
            self = lub(self, other)
        """
        other_vars = other.vars_set.difference(self.vars_set)
        common_vars = self.vars_set.intersection(other.vars_set)
        
        for v in other_vars:
            self.vars_info[v] = other.vars_info[v]
            self.vars_set.add(v)
            self.seeded_by[v] = set(other.seeded_by[v])
            self.seeds[v] = set(other.seeds[v])
        
        for v in common_vars:
            self.vars_info[v].lub_update(other.vars_info[v])
            self.seeded_by[v].update(other.seeded_by[v])
            self.seeds[v].update(other.seeds[v])
    
    def _flush_seeds(self, v):
        """
        starting from a variable v, flush everything we know about v, to all vars that points to it
        TODO think when and on what nodes do we want to call this function
        """
        working_queue = deque()
        working_queue.append(v)
        iterations = 0
        while len(working_queue):
            iterations += 1
            if iterations > 2**10:
                raise Exception("Too many iterations for function _flush_seeds") # TODO handle this case. it might be because of a loop in the graph
            v = working_queue.popleft()
            for u in self.seeds[v]:
                if self.vars_info[u].lub_update(self.vars_info[v]):
                    working_queue.append(v)
    
    def __repr__(self):
        res = ''
        for v in self.vars_set:
            res += '%s\n' %v
            vi = '\n'.join(map(lambda x: '\t%s' %x, self.vars_info[v].__repr__().splitlines()))
            res += '%s\n' %vi
        return res[:-1] # discard \n
        
        
        
        
"""

class T(object):
    def __init__(self):
        pass
        

an example about how to analyse this code:
    v = T(x = 5)
    v2 = T(x = 8, y = 9)
    v3 = T(x = 3, w = 2, z = 4)
    v2 = v3
    v3 = v

vi = VariableInfo()
vi.add_attribute('x')
vi2 = VariableInfo()
vi2.add_attribute('x')
vi2.add_attribute('y')
vi3 = VariableInfo()
vi3.add_attribute('z')
vi3.add_attribute('w')
vi3.add_attribute('x')

a = AbstractState()
a.set_var('v', vi)
a.set_var('v2', vi2)
a.set_var('v3', vi3)

a.set_var_to_var('v2', 'v3')
a.set_var_to_var('v3', 'v')

a._flush_all_seeds()

a
"""