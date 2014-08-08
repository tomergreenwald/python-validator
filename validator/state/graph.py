from collections import deque
from lattice import LatticeElement as LE

class GraphVertex(object):
    def __init__(self, ind, label):
        self.edge_label = label
        self.ind = ind
        self.parent = -1
        self.constant = -1
        self.sons = dict()
        self.knowledge = LE(LE.L_MUST_HAVE)
    
    def __repr__(self):
        return 'parent\t%d\tlabel\t%s\tconst\t%d\nknowledge\t%s\nsons\t%s' %(self.parent, self.edge_label, self.constant, self.knowledge.get_element_name(), self.sons.items())

class Graph(object):
    """
    Graph class. each vertex is labled by a non negative integer, and has:
        * single parent
        * sons
        * index of a constant it equals to
        * the label of the edge connecting it to its father
        * each vertex has an element from the lattice
    There are constants, but we save only one instance for each type
    
    the following invariants must always hold:
        par = self.vertices[son].parent => self.vertices[par].sons[self.vertices[son].edge_label] = son
        v in self.vertices.values() => v.parent >= 0 | v.constant >= 0 | v.is_top (this should be maintained by caller)
        the graph is a DAG
    """
    def __init__(self):
        self.next_ind = 0
        self.vertices = dict()
        
        self.next_cons = 0
        self.types_dict = dict()
        self.all_cons = dict()
    
    def set_vertex_to_const(self, vertex_ind, const):
        t = type(const)
        cons_ind = self.types_dict.get(t, -1)
        if cons_ind < 0:
            cons_ind = self.next_cons
            self.next_cons += 1
            self.types_dict[t] = cons_ind
            self.all_cons[cons_ind] = const
        
        self.vertices[vertex_ind].constant = cons_ind
    
    def create_new_vertex(self, label = ''):
        """
        add new vertex to the graph, returns the new vertex index
        """
        v_ind = self.next_ind
        self.next_ind += 1
        new_v = GraphVertex(v_ind, label)
        self.vertices[v_ind] = new_v
        return v_ind
    
    def make_parent(self, son, par):
        """
        connect son and parent by an edge (directed from the son to the parent)
        """
        if not self.vertices.has_key(son) or not self.vertices.has_key(par):
            raise KeyError()
            
        old_parent = self.vertices[son].parent
        if old_parent >= 0:
            self.vertices[old_parent].sons.pop(self.vertices[son].edge_label)
        
        self.vertices[son].parent = par
        self.vertices[par].sons[self.vertices[son].edge_label] = son
    
    def set_constant(self, son, cons):
        """
        set constant index for vertex
        """
        self.vertices[son].constant = cons
    
    def get_parent(self, v):
        """
        get parent index for vertex
        """
        return self.vertices[v].parent
    
    def get_constant(self, v):
        """
        get constant index for vertex
        """
        return self.vertices[v].constant
    
    def is_top(self, v):
        """
        returns true if a var is TOP
        """
        return self.vertices[v].knowledge.val == LE.L_TOP
    
    def set_top(self, v):
        """
        set a var to be TOP
        """
        self.vertices[v].knowledge.val = LE.L_TOP
    
    
    def remove_vertex(self, vertex_ind):
        """
        remove a vertex from the graph.
        make all its sons parent to be -1
        we dont remove sons from graph, because maybe someone points to them
        need to implement some kind of garbage collector
        """
        cur_v = vertex_ind
        vertex_knowledge = LE(LE.L_BOTOM)
        const_ind = -1
        path_to_const = []

        while cur_v != -1:
            if const_ind < 0 and self.vertices[cur_v].constant >= 0:
                const_ind = self.vertices[cur_v].constant
            vertex_knowledge.inplace_lub(self.vertices[cur_v].knowledge)
            if const_ind < 0:
                path_to_const.append(self.vertices[cur_v].edge_label)
            cur_v = self.vertices[cur_v].parent
        
        if const_ind >= 0:
            removed_const = self.all_cons[const_ind]
            for att in path_to_const[::-1]:
                try:
                    removed_const = removed_const.__getattribute__(att)
                except:
                    logging.debug('[remove_vertex] failed to get attribute %s from type %s' %(att, type(removed_const))
                    const_ind = -1
                    break
        
        if const_ind >= 0:
            # by this point, removed_const should refer to the type of the removed node
            for (lbl, v) in self.vertices[vertex_ind].sons:
                self.vertices[v].parent = -1
                self.vertices[v].knowledge.inplace_lub = self.vertices.knowledge
                if self.vertices[v].constant < 0:
                    if const_ind >= 0:
                        try:
                            new_const = removed_const.__getattribute__(lbl)
                            self.set_vertex_to_const(v, new_const)
                            continue
                        except:
                            logging.debug('[remove_vertex] failed to get \
                            attribute %s from type %s' %(lbl, type(removed_const))
                            
                    # we set to top in any case we were not able
                    # to determine the constant for this vertex
                    self.set_top(v)
                    
    
    def __repr__(self):
        res = ''
        for ind, ver in sorted(self.vertices.items()):
            title = '%d' %ind
            sides_len = 50 - len(title) - 2
            title = '%s %d %s' %('-' * (sides_len / 2), ind, '-' * (sides_len - sides_len / 2))
            res += '%s\n%s\n' %(title, ver)
        
        return res[:-1]
