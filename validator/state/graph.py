import logging
from lattice import LatticeElement as LE
logging.basicConfig(level = logging.DEBUG)

class SetDict(dict):
    """
    implements a dictionary that maps keys to sets
    """
    def __init__(self):
        pass
        
    def add_element(self, k, v):
        if self.has_key(k):
            self[k].add(v)
        else:
            self[k] = set([v])

class GraphEdge(object):
    def __init__(self, label = None, son = None, par = -1, know = None):
        self.label = label
        self.son = son
        self.parent = par
        self.knowledge = know if know is not None else LE(LE.L_MUST_HAVE)
    
    def __repr__(self):
        return '(%d)->(%d)\tlabel\t%s\tknowledge\t%s' \
               %(self.son, self.parent, self.label, self.knowledge)

class GraphVertex(object):
    def __init__(self, ind, label):
        self.ind = ind
        self.constant = -1
        self.bio_edge = GraphEdge(label, son = ind, par = -1)
        self.sons = SetDict()
        self.all_parents = SetDict()
        self.knowledge = LE(LE.L_MUST_HAVE)
    
    def remove_parent(self, lbl, edge):
        self.all_parents[lbl].remove(edge)
        if not self.all_parents[lbl]:
            self.all_parents.pop(lbl)
    
    def remove_son(self, lbl, edge):
        self.sons[lbl].remove(edge)
        if not self.sons[lbl]:
            self.sons.pop(lbl)
    
    def __repr__(self):
        return 'const\t%d\tknowledge\t%s\nbedge\t%s\n' %(self.constant, self.knowledge, self.bio_edge) + \
               'sons:\n%s\n' %('\n'.join(['\t%s' %x for x in self.sons.values()])) + \
               'parents:\n%s' %('\n'.join(['\t%s' %x for x in self.all_parents.values()]))

class Graph(object):
    """
    Graph class. each vertex is labelled by a non negative integer, and has:
        * single biological parent
        * possibly many step fathers
        * sons (inverse of all_parents)
        * index of a constant it equals to
        * the label of the edge connecting it to its father
        * each vertex has an element from the lattice
    There are constants, but we save only one instance for each type
    
    the following invariants must always hold:
        par = self.vertices[son].bio_parent => par in self.vertices[son].all_parents
        par in self.vertices[son].all_parents => self.vertices[par].sons[self.vertices[son].bio_label] = son
        v in self.vertices.values() => v.bio_parent >= 0 | v.constant >= 0 | v.is_top (this should be maintained by caller)
        the graph is a DAG
    """
    def __init__(self):
        self.next_ind = 0
        self.vertices = dict()
        
        self.next_cons = 0
        self.types_dict = dict()
        self.all_cons = dict()
    
    def set_vertex_to_const(self, vertex_ind, const):
        """
        set a vertex to be a constant
        add the constant to the constants pull if necessary (a constant of a new type)
        """
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
        initialize the vertex with a label. no father, no constant, not TOP
        """
        v_ind = self.next_ind
        self.next_ind += 1
        new_v = GraphVertex(v_ind, label)
        self.vertices[v_ind] = new_v
        return v_ind
    
    def make_parent(self, son, par):
        """
        this function refers to biological parent
        connect son and parent by an edge (directed from the son to the parent)
        disconnect son from parent if needed (TODO think if we are doing it right or if it is necessary at all)
        """
        if not self.vertices.has_key(son) or not self.vertices.has_key(par):
            raise KeyError()
            
        if self.vertices[son].all_parents:
            raise Exception("[make_parent] making parent of son who already has parents...")
        """
        old_parent = self.vertices[son].bio_parent
        if old_parent >= 0:
            self.vertices[old_parent].sons.pop(self.vertices[son].bio_label)
        """
        
        bedge = self.vertices[son].bio_edge
        bedge.parent = par
        # now biological edge contains all the information
        self.vertices[son].all_parents.add_element(bedge.label, bedge)
        self.vertices[par].sons.add_element(bedge.label, bedge)
    
    def make_step_parent(self, son, par, label):
        """
        this function refers to step parent (not biological)
        connect son and parent by an edge (directed from the son to the parent)
        """
        if not self.vertices.has_key(son) or not self.vertices.has_key(par):
            raise KeyError()
        
        new_edge = GraphEdge(label, son, par)
        self.vertices[son].all_parents.add_element(label, new_edge)
        self.vertices[par].sons.add_element(label, new_edge)
        
    
    def get_parent(self, v):
        """
        get biological parent index for vertex
        """
        return self.vertices[v].bio_edge.parent
    
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
        # TODO do we want to set constant to -1 and move its value to sons?
    
    def get_knowledge(self, v):
        """
        TODO rewrite this function
        returns knowledge of vertex
        """
        return self.vertices[v].knowledge
    
    def _get_rooted_const(self, vertex_ind):
        """
        received a vertex index
        return the constant which this vertex correspond to, or None if there
        is no such constant
        """
        const_ind = -1
        cur_v = vertex_ind
        path_to_const = []

        while cur_v != -1:
            if const_ind < 0 and self.vertices[cur_v].constant >= 0:
                const_ind = self.vertices[cur_v].constant
                break
            path_to_const.append(self.vertices[cur_v].bio_edge.label)
            cur_v = self.vertices[cur_v].bio_edge.parent
        
        if const_ind < 0:
            return None
        
        root_const = self.all_cons[const_ind]
        for att in path_to_const[::-1]:
            try:
                root_const = root_const.__getattribute__(att)
            except:
                logging.debug('[_get_rooted_const] failed to get attribute %s \
                                   from type %s' %(att, type(root_const)))
                return None
        
        return root_const
    
    def can_have_son(self, vertex_ind, son_label):
        """
        returns True if the son can be legally added to a vertex
        the returned value can be 'edge', 'top' or 'const', depending on
        the way we know the son can exists
        """
        if self.vertices[vertex_ind].sons.has_key(son_label):
            return 'edge')
        
        if self.is_top(vertex_ind):
            return 'top'
            
        vertex_const = self._get_rooted_const(vertex_ind)
        if vertex_const is None:
            return False
        
        try:
            son_const = vertex_const.__getattribute__(son_label)
            return 'const'
        except:
            logging.debug('[can_have_son] failed to get attribute %s \
                                   from type %s' %(son_label, type(vertex_const)))
            return False
    
    def unlink_vertex(self, vertex_ind):
        """
        unlink a vertex from all its sons, making it free
        make all its sons biological parent to be -1
        we don't remove sons from graph, because maybe someone points to them
        need to implement some kind of garbage collector to remove sons too
        this suppose to happen when this vertex is overwritten
        """
        vertex_const = self._get_rooted_const(vertex_ind)
        
        for (lbl, ee) in self.vertices[vertex_ind].sons.items():
            for e in ee:
                v = e.son
                # remove from all_parents
                self.vertices[v].remove_parent(lbl, e)
                
                if self.vertices[v].bio_edge.parent != vertex_ind:
                    # vertex belongs to another parent
                    continue
                    
                self.vertices[v].bio_edge.parent = -1
                self.vertices[v].bio_edge.label = None # just to be sure, doesn't really matter
                
                if self.vertices[v].constant < 0:
                    if vertex_const is not None:
                        try:
                            new_const = vertex_const.__getattribute__(lbl)
                            self.set_vertex_to_const(v, new_const)
                            continue
                        except:
                            logging.debug('[remove_vertex] failed to get \
                                           attribute %s from type %s' \
                                           %(lbl, type(new_const)))
                            
                    # we set to top in any case we were not able
                    # to determine the constant for this vertex
                    # this is because we can know nothing about the sons of this
                    # vertex, except if they are already exists
                    self.set_top(v)
        
        # by this point, parent of all sons is -1, and every son is TOP or
        # has a non negative constant index
        self.vertices[vertex_ind].sons.clear()
    
    def remove_vertex(self, vertex_ind):
        """
        remove a vertex from the graph. first by unlinking it from its sons, 
        then from its parent (if any)
        """
        self.unlink_vertex(vertex_ind)
        
        for (lbl, ee) in self.vertices[vertex_ind].all_parents.items():
            for e in ee:
                self.vertices[e.parent].remove_son(lbl, e)
        
        self.vertices.pop(vertex_ind)
    
    def __repr__(self):
        res = ''
        for ind, ver in sorted(self.vertices.items()):
            title = '%d' %ind
            sides_len = 50 - len(title) - 2
            title = '%s %d %s' %('-' * (sides_len / 2), ind, '-' * (sides_len - sides_len / 2))
            res += '%s\n%s\n' %(title, ver)
        
        return res[:-1]

        
        
"""
import sys
sys.path.append(r'D:\school\verify\project2\python-validator\validator\state')
execfile(r'D:\school\verify\project2\python-validator\validator\state\graph.py')

class T(object):
    def __init__(self):
        self.b = 5
        self.a = self

g = Graph(); g.create_new_vertex(); g.create_new_vertex('a'); g.make_parent(1, 0); g.create_new_vertex('a'); g.make_parent(2, 1); g.create_new_vertex('b'); g.make_parent(3, 0); g.create_new_vertex('');  g.create_new_vertex('b'); g.make_parent(5, 4); g.set_vertex_to_const(0, T())
"""