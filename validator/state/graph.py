class GraphVertex(object):
    def __init__(self, ind, label):
        self.edge_label = label
        self.ind = ind
        self.parent = -1
        self.constant = -1
        self.sons = set()
        self.is_top = False
    
    def __repr__(self):
        return 'parent\t%d\tlabel\t%s\nconst\t%d\tTOP\t%s\nsons\t%s' %(self.parent, self.edge_label, self.constant, self.is_top, list(self.sons))

class Graph(object):
    """
    Graph class. each vertex is labled by a non negative integer, and has:
        * single parent
        * sons
        * index of a constant it equals to
        * the label of the edge connecting it to its father
    each vertex can be TOP or non TOP element
    
    the following invariant must always hold:
        self.vertices[i] in self.vertices[self.vertices[i].parent].sons
        
    """
    def __init__(self):
        self.next_ind = 0
        self.vertices = dict()
    
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
            self.vertices[old_parent].sons.remove(son)
        
        self.vertices[son].parent = par
        self.vertices[par].sons.add(son)
    
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
        return self.vertices[v].is_top
    
    def set_top(self, v):
        """
        set a var to be TOP
        """
        self.vertices[v].is_top = True
    
    def unset_top(self, v):
        """
        set a var to be non TOP
        """
        self.vertices[v].is_top = False
    
    def remove_vertex(self, v):
        """
        remove a vertex from the graph
        TODO need to implement some kind of garbage collector
        """
        pass
        """
        p = self.vertices[v].parent
        if p >= 0:
            self.vertices[p].sons.remove(v)
        self.vertices.pop(v)
        """
    
    def __repr__(self):
        res = ''
        for ind, ver in sorted(self.vertices.items()):
            title = '%d' %ind
            sides_len = 40 - len(title) - 2
            title = '%s %d %s' %('-' * (sides_len / 2), ind, '-' * (sides_len - sides_len / 2))
            res += '%s\n%s\n' %(title, ver)
        
        return res[:-1]
