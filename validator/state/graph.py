import logging
from lattice import LatticeElement as LE
logging.basicConfig(level = logging.DEBUG)

class GraphVertex(object):
    def __init__(self, ind, label):
        self.bio_label = label
        self.ind = ind
        self.bio_parent = -1
        self.step_parents = set()
        self.constant = -1
        self.sons = dict()
        self.knowledge = LE(LE.L_MUST_HAVE)
    
    def __repr__(self):
        return 'bparent\t%d\tlabel\t%s\tconst\t%d\n' %(self.bio_parent, self.bio_label, self.constant) + \
               'knowledge\t%s\n' %(self.knowledge.get_element_name()) + \
               'sons\t%s\n' %(self.sons.items()) + \
               'sparents\t%s' %(self.step_parents.items())

class Graph(object):
    """
    Graph class. each vertex is labelled by a non negative integer, and has:
        * single biological parent
        * possibly many step fathers
        * sons (inverse of step_parents)
        * index of a constant it equals to
        * the label of the edge connecting it to its father
        * each vertex has an element from the lattice
    There are constants, but we save only one instance for each type
    
    the following invariants must always hold:
        par = self.vertices[son].bio_parent => par in self.vertices[son].step_parents
        par in self.vertices[son].step_parents => self.vertices[par].sons[self.vertices[son].bio_label] = son
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
            
        if self.vertices.step_parents:
            raise Exception("[make_parent] making parent of son who already has parents...")
        """
        old_parent = self.vertices[son].bio_parent
        if old_parent >= 0:
            self.vertices[old_parent].sons.pop(self.vertices[son].bio_label)
        """
        
        self.vertices[son].bio_parent = par
        self.vertices[son].step_parents.add(par)
        self.vertices[par].sons[self.vertices[son].bio_label] = son
    
    def get_parent(self, v):
        """
        get biological parent index for vertex
        """
        return self.vertices[v].bio_parent
    
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
        returns knowledge of vertex
        """
        return self.vertices[v].knowledge
    
    def get_rooted_const(self, vertex_ind):
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
            path_to_const.append(self.vertices[cur_v].bio_label)
            cur_v = self.vertices[cur_v].bio_parent
        
        if const_ind < 0:
            return None
        
        root_const = self.all_cons[const_ind]
        for att in path_to_const[::-1]:
            try:
                root_const = root_const.__getattribute__(att)
            except:
                logging.debug('[get_rooted_const] failed to get attribute %s \
                                   from type %s' %(att, type(root_const)))
                return None
        
        return root_const
    
    def can_have_son(self, vertex_ind, son_label):
        """
        returns True if the son can be legally added to a vertex
        """
        if self.is_top(vertex_ind):
            return True
            
        vertex_const = self.get_rooted_const(vertex_ind)
        if vertex_const is None:
            return False
        
        try:
            son_const = vertex_const.__getattribute__(son_label)
            return True
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
        vertex_const = self.get_rooted_const(vertex_ind)
        
        for (lbl, v) in self.vertices[vertex_ind].sons.items():
            if self.vertices[v].bio_parent != vertex_ind:
                # vertex belongs to another parent
                # TODO remove from step_parents
                continue
            self.vertices[v].parent = -1
            
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
        
        par = self.vertices[vertex_ind].bio_parent
        # TODO remove from step_parents also
        if par >= 0:
            self.vertices[par].sons.pop(self.vertices[vertex_ind].label)
        self.vertices.pop(vertex_ind)
    
    def __repr__(self):
        res = ''
        for ind, ver in sorted(self.vertices.items()):
            title = '%d' %ind
            sides_len = 50 - len(title) - 2
            title = '%s %d %s' %('-' * (sides_len / 2), ind, '-' * (sides_len - sides_len / 2))
            res += '%s\n%s\n' %(title, ver)
        
        return res[:-1]
