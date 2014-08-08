class GraphVertex(object):
    def __init__(self, ind):
        self.ind = ind
        self.parent = -1
        self.constant = -1
        self.sons = set()
        self.is_top = False

class Graph(object):
    """
    Graph class. each vertex is labled by a non negative integer, and has:
        * single parent
        * sons
        * index of a constant it equals to
    each vertex can be TOP or non TOP element
    """
    def __init__(self):
        self.size = 0
        self.vertices = dict()
    
    def create_new_vertex(self):
        """
        add new vertex to the graph, returns the new vertex index
        """
        v_ind = self.size
        self.size += 1
        new_v = GraphVertex(v_ind)
        self.vertices[v_ind] = new_v
        return v_ind
    
    def make_parent(self, son, par):
        """
        connect son and parent by an edge (directed from the son to the parent)
        """
        if not vertices.has_key(son) or not vertices.has_key(par):
            raise KeyError()
        self.vertices[son].parent = par
        self.vertices[parent].sons.add(son)
    
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