from collections import deque
from copy import copy, deepcopy
import logging
logging.basicConfig(level = logging.DEBUG)

from var_info import VariableInfo, MUST_HAVE, MUST_NOT_HAVE, MAY_HAVE
    
class AbstractState(object):
    """
    This class represents the abstract state for a set of variables (which means the abstract state for the whole program)
    it contains information about the graph of the program
    """
    def __init__(self):
        """
        we have the following members:
            vars_info: a mapping between each variable to an VariableInfo object
            vars_set: a set of all variables in vars_info, only for convenience
            seeded_by: for every variable, a list of the variables it can be seeded from (e.g. if x=y, then x is seeded by y)
            seeds: for every variable, a list of variables which is seeds (e.g. if x=y, then y seeds x. if y=z, then y stops to seed x)
            need_to_update: nodes that needs to propagate their info to their sons in the graph
        """
        self.vars_info = dict()
        self.vars_set = set()
        self.seeded_by = dict()
        self.seeds = dict()
        self.need_to_update = set()
        
    def add_var(self, var, var_info):
        """
        call this when you know some VariableInfo about var
        """
        # TODO do we need to copy var_info?
        self.vars_info[var] = deepcopy(var_info)
        self.vars_set.add(var)
        self.seeds[var] = set()
        self.seeded_by[var] = set()
    
    def clear_seeds(self, v):
        """
        propagate the knowledge we have on v towards its son
        """
        self.flush_all_seeds()
        
        for u in self.seeds[v]:
            self.seeded_by[u].remove(v)
        self.seeds[v].clear()
        
        for u in self.seeded_by[v]:
            self.seeds[u].remove(v)
        self.seeded_by[v].clear()
    
    def flush_all_seeds(self):
        """
        flush everything we know along the tree
        this function must be called before any query is made
        """
        logging.debug('flush_all_seeds')
        for v in self.need_to_update:
            logging.debug('flushing seeds from %s' %v)
            self.flush_seeds(v)
        
        self.need_to_update.clear()
    
    def _add_dependency(self, var0, var1):
        """
        var0 and var1 are the exact same instance of an object
        """
        self.seeds[var1].add(var0)
        self.seeded_by[var0].add(var1)
    
    def set_var_to_var(self, var0, var1):
        """
        call this when there is a statement var0 = var1, and var1 is a pointer (not a simple type such as integer)
        """
        self.clear_seeds(var0) # this also calls flush_all_seeds
        
        self._add_dependency(var0, var1)
        self._add_dependency(var1, var0)
        
        self.need_to_update.add(var1)
        self.need_to_update.add(var0)
        
        self.vars_info[var0] = VariableInfo()
        
        
    
    # def update_var(self, var, expression):
    
    def lub(self, other):
        """
        we take the union of both graphes (seeded_by)
        
        """
        other_vars = other.vars_set.difference(self.vars_set)
        common_vars = self.vars_set.intersection(other.vars_set)
        
        for v in other_vars:
            self.vars_info[v] = other.vars_info[v]
            self.vars_set.add(v)
            self.seeded_by[v] = set(other.seeded_by[v])
            self.seeds[v] = set(other.seeds[v])
        
        for v in common_vars:
            self.vars_info[v] = self.vars_info[v].lub_update(other.vars_info[v])
            self.seeded_by[v].update(other.seeded_by[v])
            self.seeds[v].update(other.seeds[v])
    
    def flush_seeds(self, v):
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
                raise Exception("Too many iterations for function flush_seeds") # TODO handle this case. it might be because of a loop in the graph
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

an example about how to analyse this code:
    v = T(x = 5)
    v2 = T(x = 8, y = 9)
    v3 = T(x = 3, w = 2, z = 4)
    v2 = v3
    v3 = v

vi = VariableInfo()
vi.add_attribute('x', MUST_HAVE)
vi2 = VariableInfo()
vi2.add_attribute('x', MUST_HAVE)
vi2.add_attribute('y', MUST_HAVE)
vi3 = VariableInfo()
vi3.add_attribute('z', MUST_HAVE)
vi3.add_attribute('w', MUST_HAVE)
vi3.add_attribute('x', MUST_HAVE)

a = AbstractState()
a.add_var('v', vi)
a.add_var('v2', vi2)
a.add_var('v3', vi3)

a.set_var_to_var('v2', 'v3')
a.set_var_to_var('v3', 'v')

a.flush_all_seeds()

a
"""