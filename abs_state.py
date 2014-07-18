from collections import deque
from copy import copy

from var_info import VariableInfo
    
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
        """
        self.vars_info = dict()
        self.vars_set = set()
        self.seeded_by = dict()
        self.seeds = dict()
        
    
    # def set_var_to_copy(self, var, 
    
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
            # TODO do we really need copy here?
            self.seeded_by[v] = copy(other.seeded_by[v])
            self.seeds[v] = copy(other.seeds[v])
        
        for v in common_vars:
            self.vars_info[v] = self.vars_info[v].lub_update(other.vars_info[v])
            self.seeded_by[v].extend(other.seeded_by[v])
            self.seeds[v].extend(other.seeds[v])
    
    def flush_seeds(self, v):
        working_queue = deque()
        working_queue.append(v)
        while len(working_queue):
            v = working_queue.popleft()
            for u in self.seeds[v]:
                self.