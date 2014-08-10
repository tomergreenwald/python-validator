from copy import deepcopy
from graph import Graph
from utils import *
from state_exceptions import *
from lattice import LatticeElement as LE

class AbstractState(object):
    def __init__(self):
        """
        """
        self.vars_set = set()
        self.var_to_vertex = dict()
        self.consts = dict()
        self.graph = Graph()
        self.const_count = 0
    
    def clone(self):
        """
        return a copy of the abstract state
        """
        return deepcopy(self)
    
    def add_var_and_set_to_top(self, var):
        """
        adding a variable to the state, and mark it as top
        return the vertex index of var
        """
        if var in vars_set:
            # think what should we do here... do we want to set the var to top? probably not, but remember it...
            return self.var_to_vertex[var]
        
        basename = var_to_basename[var]
        var_ind = self.graph.create_new_vertex(basename)
        self.vars_set.add(var)
        self.var_to_vertex[var] = var_ind
        self.graph.set_top(var_ind)
        
        father = var_to_father(var)
        if father:
            father_ind = self.add_var_and_set_to_top(father)
            self.graph.make_parent(var_ind, father_ind)
        
        return var_ind
        
    
    def add_var(self, var):
        """
        if var already exists- do nothing
        if father of var doesnt exist as a var- make it TOP
        otherwise- this is straight forward
        
        return the vertex index of var
        """
        if var in vars_set:
            return self.var_to_vertex[var]
            
        basename = var_to_basename[var]
        var_ind = self.graph.create_new_vertex(basename)
        self.vars_set.add(var)
        self.var_to_vertex[var] = var_ind
        
        father = var_to_father(var)
        if father is not None:
            if father not in self.vars_set:
                father_ind = self.add_var_and_set_to_top(father)
            else:
                father_ind = self.var_to_vertex[father]
                
            self.graph.make_parent(var_ind, father_ind)
    
        return var_ind
        
    def remove_var(self, var):
        """
        call this when a variable is not relevant anymore
        TODO implement some kind of garbage collector to release saved constants
        """
        """
        sons = 
        self.vars_set.remove(var)
        var_ind = self.var_to_vertex.pop(var)
        self.graph.remove_vertex(var_ind)
        """
        pass
        
    def _check_attr(self, vertex, attr):
        """
        received an index to vertex, and an attribute
        checks if this attribute belongs to the vertex
        """
    
    def expression_to_vertex_index(self, var):
        """
        receive an expression like f!g!x.a.b.c.a.b.c.a.b.c
        returns the index of the vertex corresponding to it
        logic:
            if the variable exists, returns its index
            otherwise, if there is no father, return -1
            if the father doesn't exists (recursively), return -1
            if the var cannot be a son of its father (based on TOP and constant), return -1
            if the father exists (recursively) and is TOP, create new vertex for son
            if the father exists and is not TOP, add the vertex (it must be constant-legal)
        """
        logging.debug('[expression_to_vertex_index] var %s' %var)
        if var in self.vars_set:
            return self.var_to_vertex[var]
            
        father = var_to_father(var)
        basename = var_to_basename(var)
        
        if father is None:
            # there is no father
            return -1
        else:
            # there is a father
            # we want to make sure that a vertex for the father exists (and 
            # create one if necessary)
            father_ind = self.expression_to_vertex_index(father)
            print 'created father %s with index %d' %(father, father_ind)
            if father_ind >= 0:
                if self.graph.can_have_son(father_ind, basename):
                    if self.graph.is_top(father_ind):
                        # father is TOP, so will be its son
                        return self.add_var_and_set_to_top(var) 
                    else:
                        # this must be the case that the son is legal due to constant
                        son_ind = self.graph.create_new_vertex(basename)
                        self.vars_set.add(var)
                        self.var_to_vertex[var] = son_ind
                        self.graph.make_parent(son_ind, father_ind)
                        return son_ind
                else:
                    # var cannot be son of its father
                    return -1
            else:
                # father is not part of the graph
                return -1
    
    def _get_var_index(self, var_name):
        """
        returns vertex index if we can
        may raise an exception
        """
        var_ind = self.expression_to_vertex_index(var_name)
        if var_ind < 0:
            raise VerifierError("variable %s not in state" %var_name)
        
        var_knowledge = self.graph.get_knowledge(var_ind)
        if var_knowledge.val == LE.L_MAY_HAVE:
            # TODO report this warning in another way
            logging.debug('warning var %s may not be defined' %var_name)
        
        return var_ind
    
    def _cleanup_var_vertex(self, var_name):
        """
        receives a var name. returns an index of a vertex representing this var
        and that doesn't have any sons. may raise an exception
        this creates a new vertex with L_MUST_HAVE knowledge (if needed)
        """
        var_ind = self.expression_to_vertex_index(var_name)
        if var_ind >= 0:
            # var has a representation in the graph
            # unlink it from its sons, because it may be changed very soon
            self.graph.unlink_vertex(var_ind)
            return var_ind
        
        basename = var_to_basename(var_name)
        father = var_to_father(var_name)
        if father is None:
            # there is no father. var is without attributes
            var_ind = self.graph.create_new_vertex(var_name)
            self.vars_set.add(var_name)
            self.var_to_vertex[var_name] = var_ind
            return var_ind
        else:
            # the following line may raise an Exception
            father_ind = self._get_var_index(father)
            # this is the case when we create new attribute
            var_ind = self.graph.create_new_vertex(basename)
            self.vars_set.add(var_name)
            self.var_to_vertex[var_name] = var_ind
            self.graph.make_parent(var_ind, father_ind)
            return var_ind
            
    
    def set_var_to_const(self, var_name, val):
        """
        call this function when a by-value assignment is done, such as x = 5
        we expect val0 to consist of a known type during analysis time
        """
        logging.debug('set var %s to const' %var_name)
        
        var_ind = self._cleanup_var_vertex(var_name)
        self.graph.set_vertex_to_const(var_ind, val)
    
    def set_var_to_var(self, var0, var1):
        """
        call this when there is a statement var0 = var1, and var1 is a pointer (not 
        a simple type such as integer)
        """
        logging.debug('set var %s to %s' %(var0, var1))
        
        var1_ind = self._get_var_index(var1)
        
        """
        var0_ind = self.expression_to_vertex_index(var0)
        if var0_ind >= 0:
            # var has a representation in the graph
            # unlink it from its sons, because it may be changed very soon
            self.graph.unlink_vertex(var0_ind)
        
        father0 = var_to_father(var0)
        if father0 is None:
            # there is no father. var is without attributes
            pass
        else:
            father0_ind = self._get_var_index(father0)
            if var0_ind < 0:
                var0_ind = this.graph.create_new_vertex(basename)
            self.make_parent(
        
        
        
        
        if var0 not in self.vars_set:
            # new variable will be created
            
            father0 = var_to_father(var0)
            if father0 is not None:
                if father0 in self.vars_set:
                    father0_ind = self.var_to_vertex[father0]
                else:
                    # TODO think what we need to do here: create new father or
                    # report an alert? in the first case, we may use add_var instead
                    father0_ind = self.add_var_and_set_to_top(father0)
                    
                self.graph.make_parent(var0_ind, father0_ind)
            else:        
                var0_ind = self.add_var(var0)
        else:
            
            
            self.vars_set.add(var0)
            self.seeds[var0] = set()
            self.seeded_by[var0] = set()
        
            
        self._clear_seeds(var0) # this also calls _flush_all_seeds
        
        self._add_dependency(var0, var1)
        self._add_dependency(var1, var0)
        
        self.need_to_update.add(var1)
        self.need_to_update.add(var0)
        
        self.vars_info[var0] = VariableInfo()
    """
    