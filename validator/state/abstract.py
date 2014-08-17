from copy import deepcopy
import logging
from graph import Graph
from utils import *
from state_exceptions import *
from lattice import LatticeElement as LE

"""
TODO we dont really want to save all the vars in var_to_vertex, unless they are main vars (no attributes)
TODO when querying for some var and the result is not L_MUST_HAVE, consider changing the full path to L_MUST_HAVE
"""

class AbstractState(object):
    def __init__(self):
        """
        """
        self.vars_set = set()
        # TODO think if var_to_vertex should contain only main var names
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
        var_ind = self._expression_to_vertex_index(var)
        if var_ind >= 0:
            # think what should we do here... do we want to set the var to top? probably not, but remember it...
            # self.graph.set_top(var_ind)
            return var_ind
        
        
        basename = var_to_basename(var)
        var_ind = self.graph.create_new_vertex(basename)
        self.graph.set_top(var_ind)
        
        father = var_to_father(var)
        if father:
            father_ind = self.add_var_and_set_to_top(father)
            self.graph.make_bio_parent(var_ind, father_ind)
        else:
            self.vars_set.add(var)
            self.var_to_vertex[var] = var_ind
        
        return var_ind
        
    """
    def add_var(self, var):
        "" "
        if var already exists- do nothing
        if father of var doesnt exist as a var- make it TOP
        otherwise- this is straight forward
        
        return the vertex index of var
        "" "
        if var in vars_set:
            return self.var_to_vertex[var]
            
        basename = var_to_basename(var)
        var_ind = self.graph.create_new_vertex(basename)
        self.vars_set.add(var)
        self.var_to_vertex[var] = var_ind
        
        father = var_to_father(var)
        if father is not None:
            if father not in self.vars_set:
                father_ind = self.add_var_and_set_to_top(father)
            else:
                father_ind = self.var_to_vertex[father]
                
            self.graph.make_bio_parent(var_ind, father_ind)
    
        return var_ind
    """
    
    def remove_var(self, var):
        """
        call this when a variable is not relevant anymore
        TODO implement some kind of garbage collector to release saved constants
        """
        pass
        
    def _check_attr(self, vertex, attr):
        """
        received an index to vertex, and an attribute
        checks if this attribute belongs to the vertex
        """
    
    def _expression_to_vertex_index(self, var):
        """
        receive an expression like f!g!x.a.b.c.a.b.c.a.b.c
        returns the index of the vertex corresponding to it
        logic:
            if the variable exists in vars_set, returns its index
            otherwise, if there is no semantic father, return -1
            if the father doesn't exists in the graph (recursively), return -1
            if the var cannot be a son of its father (based on TOP, constant and edge), return -1
            if the var is already son in the graph, returns its vertex index
            if the father is TOP, create new vertex for son
            if the father is not TOP, add the vertex (it must be constant-legal)
        """
        logging.debug('[_expression_to_vertex_index] var %s' %var)
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
            father_ind = self._expression_to_vertex_index(father)
            if father_ind >= 0:
                have_son = self.graph.can_have_son(father_ind, basename)
                if have_son:
                    if have_son == 'top':
                        # father is TOP, so will be its son
                        return self.add_var_and_set_to_top(var) 
                    elif have_son == 'const':
                        # this must be the case that the son is legal due to constant
                        son_ind = self.graph.create_new_vertex(basename)
                        self.graph.make_bio_parent(son_ind, father_ind)
                        return son_ind
                    elif have_son == 'edge':
                        # this must be the case that the son already exists in the graph
                        son_ind = self.graph.get_son_index(father_ind, basename)
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
        var_ind = self._expression_to_vertex_index(var_name)
        if var_ind < 0:
            raise VerifierError("variable %s not in state" %var_name)
        
        var_knowledge = self.graph.get_knowledge(var_ind)
        if var_knowledge.val == LE.L_MAY_HAVE:
            # TODO report this warning in another way
            # TODO consider the edges that leads to the vertex
            logging.debug('warning var %s may not be defined' %var_name)
        
        return var_ind
    
    def _cleanup_var_vertex(self, var_name):
        """
        receives a var name. returns an index of a vertex representing this var
        and that doesn't have any sons. may raise an exception
        this can create a new vertex with L_MUST_HAVE knowledge if the var
        doesn't exist
        """
        var_ind = self._expression_to_vertex_index(var_name)
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
            self.graph.make_bio_parent(var_ind, father_ind)
            return var_ind
            
    
    def set_var_to_const(self, var_name, val):
        """
        call this function when a by-value assignment is done, such as x = 5
        we expect val0 to consist of a known type during analysis time
        """
        logging.debug('[set_var_to_const] set var %s to const' %var_name)
        
        var_ind = self._cleanup_var_vertex(var_name)
        self.graph.set_vertex_to_const(var_ind, val)
    
    def set_var_to_var(self, var0, var1):
        """
        call this when there is a statement var0 = var1, and var1 is a pointer (not 
        a simple type such as integer)
        """
        logging.debug('[set_var_to_var] set var %s to %s' %(var0, var1))
        
        # following line may raise an exception
        var1_ind = self._get_var_index(var1)
        
        try:
            var0_ind = self._get_var_index(var0)
        except VerifierError:
            var0_ind = -1
        
        father0_ind = -1
        father_var0 = var_to_father(var0)
        if father_var0 is not None:
            # semantic father exists
            try:
                father0_ind = self._get_var_index(father_var0)
            except VerifierError:
                raise VerifierError("Cannot set var %s because %s doesn't exist" %(var0, father_var0))
        
        if var0_ind < 0:
            # set var0 to point to var1 vertex
            # create new step father if needed
            basename = var_to_basename(var0)
            if father0_ind >= 0:
                self.graph.make_step_parent(var1_ind, father0_ind, basename)
            else:
                self.vars_set.add(var0)
                self.var_to_vertex[var0] = var1_ind
        else:
            # make the children of the vertex independent of him
            self.graph.unlink_vertex(var0_ind)
            
            if father0_ind >= 0:
                basename = var_to_basename(var0)
                self.var_to_vertex[var0] = var1_ind
                if father0_ind >= 0:
                    self.graph.make_step_parent(var1_ind, father0_ind, basename)
            else:
                # simply change the vertex for this var
                self.var_to_vertex[var0] = var1_ind
            
        
        
        
    
"""
import sys; sys.path.append(r'D:\school\verify\project2\python-validator\validator\state'); execfile(r'D:\school\verify\project2\python-validator\validator\state\abstract.py')

class T(object):
    def __init__(self):
        self.b = 5
        self.a = self

a = AbstractState(); a.set_var_to_const('x', T()); a.set_var_to_var('z', 'x.a.a.a.b.real.real'); a.set_var_to_const('y', Exception()); a.set_var_to_var('x.a.a.a.b', 'y.message'); 

a._get_var_index('x.a.a.a.b.real')

"""