from copy import deepcopy
import logging
from graph import Graph, SonKnowledge
from utils import *
from state_exceptions import *
from lattice import LatticeElement as LE

logging.basicConfig(level = logging.DEBUG)

ROOT_VERTEX = 0

class AbstractState(object):
    """
    API methods:
        returns list of errors:
            remove_var(var_name)
            query(var_name)
            set_var_to_const(var_name, val)
            set_var_to_var(var0, var1)
        other functions:
            add_var_and_set_to_top(var_name)
            lub(other)
            clone()
    """
    def __init__(self):
        """
        """
        self.vars_set = set()
        self.var_to_vertex = dict()
        self.graph = Graph()
    
    def clone(self):
        """
        return a copy of the abstract state
        """
        logging.debug('[clone]')
        return deepcopy(self)
    
    def add_var_and_set_to_top(self, var, given_father = -1):
        """
        adding a variable to the state, and mark it as top
        return the vertex index of var
        if given_father is not -1, then the function assumes that var is son of given_father
        """
        logging.debug('[add_var_and_set_to_top] var %s' %var)
        basename = var_to_basename(var)
        father = var_to_father(var)
        
        if given_father < 0:
            var_ind = self._expression_to_vertex_index(var)
            if var_ind >= 0:
                # think what should we do here... do we want to set the var to top? probably not, but remember it...
                # self.graph.set_top(var_ind)
                return var_ind
        
            if father:
                father_ind = self.add_var_and_set_to_top(father)
            else:
                father_ind = ROOT_VERTEX
        else:
            father_ind = given_father
        
        var_ind = self.graph.create_new_vertex(father_ind, basename)
        self.graph.set_top(var_ind)
        
        return var_ind
    
    def remove_var(self, var, add_tops = True):
        """
        call this when a variable is not relevant anymore
        if add_tops is True, the path to this vertex will be considered as L_MUST_HAVE
        """
        logging.debug('[remove_var] var %s' %var)
        
        (i, r) = self._get_var_index(var, add_tops)
        
        if i >= 0:
            fathers = self._split_to_fathers(var)
            
            need_to_unlink = True
            for f in fathers[:-1]:
                j = self._expression_to_vertex_index(f)
                if not self.graph.is_single_son(j):
                    need_to_unlink = False
                    break
            
            if need_to_unlink:
                father = var_to_father(var)
                basename = var_to_basename(var)    
                father_ind = self._expression_to_vertex_index(father)
            
                self.graph.unlink_single_son(father_ind, basename)
        
        # if i >= 0:
        #     self.graph.remove_vertex(i)
        return r
    
    def _expression_to_vertex_index(self, var):
        """
        receive an expression like f#g#x.a.b.c.a.b.c.a.b.c
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
        # logging.debug('[_expression_to_vertex_index] var %s' %var)
        if var == '':
            return ROOT_VERTEX
            
        father = var_to_father(var)
        basename = var_to_basename(var)
        
        if father == '':
            # if no father exists, father is the root of the graph
            father_ind = ROOT_VERTEX
        else:
            # we want to make sure that a vertex for the father exists (and 
            # create one if necessary)
            father_ind = self._expression_to_vertex_index(father)
            
        if father_ind >= 0:
            have_son = self.graph.can_have_son(father_ind, basename)
            if have_son != SonKnowledge.FALSE:
                if have_son == SonKnowledge.TOP:
                    # father is TOP, so will be its son
                    return self.add_var_and_set_to_top(var, father_ind) 
                elif have_son == SonKnowledge.CONST or have_son == SonKnowledge.MAYBE_CONST:
                    # this must be the case that the son is legal due to constant
                    son_ind = self.graph.create_new_vertex(father_ind, basename)
                    self.graph.propagate_const_to_son(father_ind, basename)
                    return son_ind
                elif have_son == SonKnowledge.EDGE:
                    # this must be the case that the son already exists in the graph
                    son_ind = self.graph.get_son_index(father_ind, basename)
                    return son_ind
            else:
                # var cannot be son of its father
                return -1
        else:
            # father is not part of the graph
            return -1
    
    def query(self, var_name, add_tops = True):
        """
        returns list of possible errors and alerts when querying a
        variable/attribute.
        if add_tops is True, then the graph is fixed, so the variable
        will exists legally in the graph
        """
        logging.debug('[query] var %s' %var_name)
        (i, r) = self._get_var_index(var_name, add_tops)
        return r
    
    def _split_to_fathers(self, var_name):
        fathers = []
        f = var_name
        while f != '':
            fathers.append(f)
            f = var_to_father(f)
        
        return fathers[::-1]
    
    def _get_var_index(self, var_name, add_tops = True):
        """
        returns vertex index if we can
        returns list of possible errors and alerts
        if add_tops is True, add unknown variables as TOPs
        """
        res = []
        
        fathers = self._split_to_fathers(var_name)
        
        # now fathers contains the full chain to var_name
        for f in fathers:
            ind = self._expression_to_vertex_index(f)
            if ind < 0:
                res.append(("Error", "var %s attribute %s" %(var_to_father(f), var_to_basename(f))))
                if add_tops:
                    self.add_var_and_set_to_top(f)
                else:
                    return (-1, res)
            else:
                old_f = var_to_father(f)
                basename = var_to_basename(f)
                old_f_ind = self._expression_to_vertex_index(old_f)
                
                son_knowledge = self.graph.get_son_knowledge(old_f_ind, basename)
                
                if son_knowledge.val != LE.L_MUST_HAVE:
                    res.append(("Alert", "var %s attribute %s" %(var_to_father(f), var_to_basename(f))))
                    if add_tops:
                        # change knowledge of edge to be L_MUST_HAVE
                        self.graph.set_son_knowledge_to_must(old_f_ind, basename)
                    
        
        return (self._expression_to_vertex_index(var_name), res)
    
    def _test_father_mutability(self, father_name, father_ind, add_tops = True):
        """
        call this before adding an attribute to a vertex, to test
        its mutability
        if add_tops is True, then the mutability will be set to L_MUST_HAVE
        """
        errors = []
        mutable = self.graph.get_mutable(father_ind)
        fix_mutable = False
        
        if mutable.val == LE.L_MUST_NOT_HAVE:
            errors.append(("Error", "var %s is immutable" %(father_name)))
            fix_mutable = True
        elif mutable.val == LE.L_MAY_HAVE:
            errors.append(("Alert", "var %s might be immutable" %(father_name)))
            fix_mutable = True
        
        if add_tops and fix_mutable:
            self.graph.set_mutable(father_ind)
        
        return errors
    
    def _cleanup_var_vertex(self, var_name):
        """
        receives a var name. returns an index of a vertex representing this var
        and that doesn't have any sons. may raise an exception
        this can create a new vertex with L_MUST_HAVE knowledge if the var
        doesn't exist
        returns (var_ind, errors) where errors is a list of possible errors and alerts
        """
        var_ind = self._expression_to_vertex_index(var_name)
        if var_ind >= 0:
            # var has a representation in the graph
            # unlink it from its sons, because it may be changed very soon
            self.graph.unlink_vertex(var_ind)
            return var_ind, []
        
        # we need to create a new vertex
        basename = var_to_basename(var_name)
        father = var_to_father(var_name)
        
        if father == '':
            # there is no father. var is main variable
            father_ind = ROOT_VERTEX
            errors = []
        else:
            # this is the case when we create new attribute
            father_ind, errors = self._get_var_index(father)
        
        # check if father is mutable
        m_errors = self._test_father_mutability(father, father_ind)
        errors.extend(m_errors)
        
        var_ind = self.graph.create_new_vertex(father_ind, basename)
        return var_ind, errors
            
    
    def set_var_to_const(self, var_name, val):
        """
        call this function when a by-value assignment is done, such as x = 5
        we expect val0 to consist of a known type during analysis time
        returns list of errors and alerts
        """
        logging.debug('[set_var_to_const] set var %s to const' %var_name)
        
        var_ind, errors = self._cleanup_var_vertex(var_name)
        self.graph.set_vertex_to_const(var_ind, val)
        
        return errors
    
    def set_var_to_var(self, var0, var1):
        """
        call this when there is a statement var0 = var1, and var1 is a pointer (not 
        a simple type such as integer)
        """
        logging.debug('[set_var_to_var] set var %s to %s' %(var0, var1))
        
        errors = []
        
        var1_ind, errors1 = self._get_var_index(var1)
        errors.extend(errors1)
        
        father_var0 = var_to_father(var0)
        father0_ind, errors0 = self._get_var_index(father_var0)
        errors.extend(errors0)
        
        basename = var_to_basename(var0)
        
        var0_ind = self._expression_to_vertex_index(var0)
        
        if var0_ind >= 0:
            # vertex already exists
            self.graph.unlink_single_son(father0_ind, basename)
        else:
            # check if father is mutable
            m_errors = self._test_father_mutability(father_var0, father0_ind)
            errors.extend(m_errors)
        
        # set var0 to point to var1 vertex
        # create new step father
        self.graph.make_parent(var1_ind, father0_ind, basename)
        
        return errors
            
    def collect_garbage(self):
        """
        remove unused vertices from the graph
        """
        self.graph.collect_garbage()
        
    def lub(self, other):
        """
        perform inplace lub (self = lub(self, other))
        """
        logging.debug('[lub]' %var_name)
        self.graph.fill_graphs(other.graph)
        
        # this is a good point to get rid of unused vertices and constants
        self.collect_garbage()
        other.collect_garbage()
        
        # rename the vertices and constant names, so that vertex at index 1 
        # and constant at index 0 will be next vertex/constant of other/self
        self.rename_indices(other)
        
        self.graph.lub(other.graph)
    
    def rename_indices(self, other):
        """
        rename vertices and constants indices of self and other,
        so there will be no mutual indices
        """
        if self.graph.next_ind >= other.graph.next_ind:
            other.graph.rename_vertices_offset(self.graph.next_ind - 1)
        else:
            self.graph.rename_vertices_offset(other.graph.next_ind - 1)
        
        if self.graph.next_cons >= other.graph.next_cons:
            other.graph.rename_constants_offset(self.graph.next_cons)
        else:
            self.graph.rename_constants_offset(other.graph.next_cons)
    
    def add_state(self, other):
        """
        add another state to the current state, possibly overriding existing 
        variables
        """
        logging.debug('[add_state]' %var_name)
        main_vars = other.graph.get_main_vars()
        for var_name in main_vars:
            # remove main variable from graph
            self.remove_var(var_name, False)
        
        # prepare to merge the two graphs...
        self.collect_garbage()
        other.collect_garbage()
        self.rename_indices(other)
        
        self.graph.add_graph(other.graph)
        
    def register_method_metadata(self, var_name, method_name, metadata):
        """
        add metadata to a variable name, to be associated with method method_name
        """
        logging.debug('[register_method_metadata] var %s method %s' %(var_name, method_name))
        
        # var_ind, errors = self._get_var_index(var_name)
        errors = []
        
        def some_func():
            pass
        
        new_method_name = '%s.%s' %(var_name, method_name)
        errors.extend(self.set_var_to_const(new_method_name, some_func))
        var_ind, errors2 = self._get_var_index(new_method_name)
        errors.extend(errors2)
        
        self.graph.add_metadata_testing(var_ind, metadata)
        self.graph.set_callable(var_ind)
        
        return errors
    
    def get_method_metadata(self, var_name, method_name):
        """
        returns a set of possible metadatas associated with method_name of var_name
        """
        logging.debug('[get_method_metadata] var %s' %var_name)
        method_name = '%s.%s' %(var_name, method_name)
        
        var_ind, errors = self._get_var_index(method_name)
        callable = self.graph.get_callable(var_ind)
        res = self.graph.get_metadata_testing(var_ind)
        
        # TODO do we want to mark this vertex as callable? probably yes, but with what metadata?
        if callable.val == LE.L_MUST_NOT_HAVE:
            errors.append(("Error", "method %s is not callable" %(method_name)))
        elif callable.val == LE.L_MAY_HAVE:
            errors.append(("Alert", "method %s might be uncallable" %(method_name)))
        
        return (res, errors)
    
"""
import sys; sys.path.append(r'D:\school\verify\project2\python-validator\validator\state'); execfile(r'D:\school\verify\project2\python-validator\validator\state\abstract.py')

class T(object):
    def __init__(self):
        self.b = 5
        self.a = self

a = AbstractState(); a.set_var_to_const('x', T()); a.set_var_to_var('z', 'x.a.a.a.b.real.real'); a.set_var_to_const('y', Exception()); a.set_var_to_var('x.a.a.a.b', 'y.message'); 

a._get_var_index('x.a.a.a.b.real')


a = AbstractState(); a.set_var_to_const('x', 'aviel'); a._get_var_index('x.index'); a.set_var_to_const('x.t', 5); a2 = AbstractState(); a2.set_var_to_const('x', 'afdsfds'); a2.set_var_to_const('x.t', 5.6); a2.set_var_to_var('y', 'x.t')


a = AbstractState(); a.set_var_to_const('x', object()); a2 = AbstractState(); a2.set_var_to_const('x', Exception()); a.lub(a2)


"""