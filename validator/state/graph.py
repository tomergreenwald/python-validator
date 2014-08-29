import logging
import copy
from collections import deque
from lattice import LatticeElement as LE
from utils import MyNone
# logging.basicConfig(level = logging.DEBUG)

"""
TODO
(maybe) need to solve the problem where a constant refers to itself
"""

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
    def __init__(self, label = None, son = None, par = 0, know = None):
        self.label = label
        self.son = son
        self.parent = par
        self.knowledge = copy.copy(know) if know is not None else LE(LE.L_MUST_HAVE)
    
    def __repr__(self):
        return '(%d)->(%d)\tlabel\t%s\tknowledge\t%s' \
               %(self.son, self.parent, self.label, self.knowledge)

class GraphVertex(object):
    def __init__(self, ind, label):
        self.ind = ind
        self.constant = -1
        self.sons = dict()
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
        return 'const\t%d\tknowledge\t%s\n' %(self.constant, self.knowledge) + \
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
        edge in self.vertices[son].all_parents => edge.son = son, edge in self.vertices[edge.par].sons[edge.label]
        edge in self.vertices[par].sons => edge.par = par, edge in self.vertices[edge.son].all_parents[edge.label]
        edge = self.vertices[son].bio_edge => edge in self.vertices[son].all_parents
        v in self.vertices.values() => v.bio_edge.par >= 0 | v.constant >= 0 | v.is_top (this should be maintained by caller)
        the graph is a DAG
    """
    def __init__(self):
        self.next_ind = 0
        self.vertices = dict()
        
        self.next_cons = 0
        self.types_dict = dict()
        self.all_cons = dict()
        
        self.create_new_vertex(label = '')
    
    def set_vertex_to_const(self, vertex_ind, const):
        """
        set a vertex to be a constant
        add the constant to the constants pull if necessary (a constant of a new type)
        mark this vertex as non top
        """
        t = type(const)
        cons_ind = self.types_dict.get(t, -1)
        if cons_ind < 0:
            cons_ind = self.next_cons
            self.next_cons += 1
            self.types_dict[t] = cons_ind
            self.all_cons[cons_ind] = const
        
        self.vertices[vertex_ind].constant = cons_ind
        # new var won't be top
        self.vertices[vertex_ind].knowledge = LE(LE.L_MUST_HAVE)
    
    def create_new_vertex(self, parent = 0, label = ''):
        """
        add new vertex to the graph, returns the new vertex index
        initialize the vertex with a label. no father, no constant, not TOP
        """
        v_ind = self.next_ind
        self.next_ind += 1
        new_v = GraphVertex(v_ind, label)
        self.vertices[v_ind] = new_v
        
        self.make_parent(v_ind, parent, label)
        
        return v_ind
    
    def make_parent(self, son, par, label, know = None):
        """
        this function refers to step parent (not biological)
        connect son and parent by an edge (directed from the son to the parent)
        """
        if not self.vertices.has_key(son) or not self.vertices.has_key(par):
            raise KeyError()
        
        new_edge = GraphEdge(label, son, par, know)
        self.vertices[son].all_parents.add_element(label, new_edge)
        
        if self.vertices[par].sons.has_key(label):
            self.unlink_single_son(par, label)
        self.vertices[par].sons[label] = new_edge
    
    def is_top(self, v):
        """
        returns true if a var is TOP
        """
        return self.vertices[v].knowledge.val == LE.L_TOP
    
    def set_top(self, v):
        """
        set a var to be TOP
        set its constant to be -1
        """
        self.vertices[v].knowledge.val = LE.L_TOP
        self.vertices[v].constant = -1
        # TODO do we want to mark all its sons edges to L_MAY_HAVE? currently not, becuase
        # this function is called only on new vertices, but we need to reconsider this
    
    def _get_rooted_const(self, vertex_ind):
        """
        received a vertex index
        return the constant which this vertex correspond to, or MyNone if there
        is no such constant
        """
        cons_ind = self.vertices[vertex_ind].constant
        vertex_const = self.all_cons.get(cons_ind, MyNone())
        
        return vertex_const
    
    def get_son_index(self, par, lbl):
        """
        return vertex index of son of par which has label lbl
        """
        if self.vertices[par].sons.has_key(lbl):
            return self.vertices[par].sons[lbl].son
        return -1
    
    def get_son_knowledge(self, par, lbl):
        """
        like get_son_index, but instead of returning the son index, returns the knowledge of that edge
        """
        if self.vertices[par].sons.has_key(lbl):
            return self.vertices[par].sons[lbl].knowledge
        assert False
    
    def set_son_knowledge_to_must(self, par, lbl):
        """
        set the knowledge of an edge labelled lbl, with parent par, to be L_MUST_HAVE
        """
        if self.vertices[par].sons.has_key(lbl):
            self.vertices[par].sons[lbl].knowledge.val = LE.L_MUST_HAVE
        assert False
    
    def propagate_const_to_son(self, vertex_ind, son_label):
        cons_ind = self.vertices[vertex_ind].constant
        son_ind = self.vertices[vertex_ind].sons[son_label].son
        
        if cons_ind < 0:
            return
            
        vertex_const = self.all_cons[cons_ind]
        
        try:
            son_const = vertex_const.__getattribute__(son_label)
        except Exception:
            return
        
        self.set_vertex_to_const(son_ind, son_const)
    
    def can_have_son(self, vertex_ind, son_label):
        """
        returns True if the son can be legally added to a vertex
        the returned value can be 'edge', 'top' or 'const', depending on
        the way we know the son can exists
        """
        if self.vertices[vertex_ind].sons.has_key(son_label):
            return 'edge'
        
        if self.is_top(vertex_ind):
            return 'top'
            
        vertex_const = self._get_rooted_const(vertex_ind)
        if isinstance(vertex_const, MyNone):
            return False
        
        try:
            son_const = vertex_const.__getattribute__(son_label)
            return 'const'
        except Exception:
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
        
        for lbl in self.vertices[vertex_ind].sons.keys():
            self.unlink_single_son(vertex_ind, lbl)
    
    def unlink_single_son(self, vertex_ind, son_label):
        """
        propagate constant from father to single son
        """
        if not self.vertices[vertex_ind].sons.has_key(son_label):
            return
        
        edge = self.vertices[vertex_ind].sons[son_label]
        v = edge.son
        lbl = son_label
        
        # remove from all_parents
        self.vertices[v].remove_parent(lbl, edge)
        self.vertices[vertex_ind].sons.pop(son_label)
        
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
        
    def collect_garbage(self):
        """
        remove unused vertices from the graph
        a vertex is in use if there is a path from it to the root vertex, or if it is a biological parent
        of any vertex which is in use
        also calls to compress indices to decrease vertices indices as can
        """
        used_vertices = set([0])
        q = deque([0])
        
        while len(q):
            v = q.popleft()
            neis = [edge.son for edge in self.vertices[v].sons.values()]
                
            for u in neis:
                if u not in used_vertices:
                    used_vertices.add(u)
                    q.append(u)
        
        for v in self.vertices.keys():
            for l, ee in self.vertices[v].all_parents.items():
                new_ee = set()
                for e in ee:
                    if e.parent < 0 or e.parent in used_vertices:
                        new_ee.add(e)
                self.vertices[v].all_parents[l] = new_ee
                        
            if v not in used_vertices:
                self.vertices.pop(v)
        
        # rename vertices so that indices will be compressed
        self.compress_indices()
        
        # throw away constant that are not in use
        used_constant = set()
        for ver in self.vertices.values():
            if ver.constant >= 0:
                used_constant.add(ver.constant)
        
        for t, i in self.types_dict.items():
            if i not in used_constant:
                self.types_dict.pop(t)
        
        for i in self.all_cons.keys():
            if i not in used_constant:
                self.all_cons.pop(i)
        
        # compress constant indices
        c_mapping = dict(zip(sorted(self.all_cons.keys()), range(len(self.all_cons))))
        self.rename_constants_indices(c_mapping)
        self.next_cons = max(self.all_cons.keys()) + 1
    
    def compress_indices(self):
        """
        rename vertices names so the indices will be compressed
        """
        mapping = self.build_compressed_mapping()
        self.rename_vertices_indices(mapping)
        self.next_ind = max(self.vertices.keys()) + 1
    
    def rename_vertices_offset(self, offset):
        """
        rename each vertex index:
            x <- x + offset
        root vertex remain to be index 0
        """
        mapping = dict([(x, x + offset) for x in self.vertices.keys()])
        self.rename_vertices_indices(mapping)
    
    def build_compressed_mapping(self):
        """
        returns dict from set like 0,1,4,5,8 to be 0,1,2,3,4
        """
        keys = sorted(self.vertices.keys())
        vals = range(len(keys))
        
        return dict(zip(keys, vals))
    
    def rename_vertices_indices(self, mapping):
        """
        rename each vertex index:
            x <- mapping[x]
        root vertex remain to be index 0
        """
        # go over all parents
        for v in self.vertices.keys():
            for ee in self.vertices[v].all_parents.values():
                for e in ee:
                    if e.parent > 0:
                        e.parent = mapping.get(e.parent, e.parent)
                    if e.son > 0:
                        e.son = mapping.get(e.son, e.son)
            
        new_vertices = dict()
        for v in self.vertices.keys():
            gv = self.vertices.pop(v)
            
            if v == 0:
                new_vertices[0] = gv
            else:
                new_vertices[mapping.get(v, v)] = gv
        
        self.vertices = new_vertices
        self.next_ind = max(self.vertices.keys()) + 1
    
    def rename_constants_indices(self, mapping):
        """
        rename each constant index:
            x <- mapping[x]
        """
        for v in self.vertices.keys():
            if self.vertices[v].constant >= 0:
                self.vertices[v].constant = mapping.get(self.vertices[v].constant, self.vertices[v].constant)
        
        new_all_cons = dict()
        for c in self.all_cons.keys():
            cv = self.all_cons.pop(c)
            new_all_cons[mapping.get(c, c)] = cv
        self.all_cons = new_all_cons
        
        for t in self.types_dict.keys():
            self.types_dict[t] = mapping.get(self.types_dict[t], self.types_dict[t])
        
        self.next_cons = max(self.all_cons.keys()) + 1
    
    def rename_constants_offset(self, offset):
        """
        rename each constant index:
            x <- x + offset
        """
        mapping = dict([(x, x + offset) for x in self.all_cons.keys()])
        self.rename_constants_indices(mapping)
    
    def vertex_lub(self, x, other, y):
        """
        lub between self.vertices[x] and other.vertices[y]
        """
        v0 = self.vertices[x]
        v1 = other.vertices[y]
        
        v0.knowledge.inplace_lub(v1.knowledge)
        
        if v0.constant != v1.constant:
            # TODO make a set of all possible constants
            # v0.constant = -1
            # v0.knowledge = LE(LE.L_TOP)
            self.set_top(x)
    
    def _handle_common_edges(self, edge_pairs):
        """
        lub between any two edges
        first element is edge of self, second element is edge of other
        """
        for (e0, e1) in edge_pairs:
            e0.knowledge.inplace_lub(e1.knowledge)
    
    def _find_common_vertices_and_edges(self, other, common_vertices, common_edges, vertices_pairs):
        """
        result:
            common_vertices: common vertices between self graph and other graph
            common_edges: common edges between self graph and other graph
            vertices_pairs: pairs (y,x) of vertices in cartesian(other.vertices.keys(), self.vertices.keys())
                            which are the same vertices
        """
        common_vertices.add(0)
        
        q = deque([(0, 0)])
        # go over the whole graph to find common vertices and edges
        while len(q):
            (x, y) = q.popleft()
            vertices_pairs.add((y, x))
            common = set(self.vertices[x].sons.keys()).intersection(other.vertices[y].sons.keys())
            for c in common:
                e0 = self.vertices[x].sons[c]
                e1 = other.vertices[y].sons[c]
                common_edges.add((e0, e1))
                s0 = e0.son
                s1 = e1.son
                if s0 != 0 and s1 != 0:
                    q.append((s0, s1))
                    common_vertices.add(s0)
                    common_vertices.add(s1)
    
    def _merge_cons(self, other):
        """
        merge constant indices between self and other, if the constant are of the same type
        modifies other's constants
        """
        cons_pairs = []
        for t,i in self.types_dict.items():
            other_ind = other.types_dict.get(t, -1)
            if other_ind >= 0:
                cons_pairs.append((other_ind, i))
        
        other.rename_constants_indices(dict(cons_pairs))
    
    def _add_other_graph(self, other, common_vertices):
        """
        add to self graph vertices and edges that are in other graph
        """
        for v in other.vertices.keys():
            if v not in common_vertices:
                # create new vertex from others
                self.vertices[v] = other.vertices[v]
                
            # go over all edges of other graph, and if they are not common, lub their knowledge with L_MAY_HAVE
            for ee in other.vertices[v].all_parents.values():
                for e in ee:
                    son_common = e.son in common_vertices
                    parent_common = e.parent in common_vertices
                    
                    if son_common and parent_common:
                        # by this point, vertices had already been renamed
                        # check if this vertex exists also in self graph
                        if self.vertices[e.parent].sons.has_key(e.label):
                            if self.vertices[e.parent].sons[e.label].son != e.son:
                                assert False
                            # edge already exists in self graph, so this will be handled somewhere
                            pass
                        else:
                            # this edge is new, but connects two common vertices
                            self.make_parent(e.son, e.parent, e.label, LE(LE.L_MAY_HAVE))
                    else:
                        e.knowledge.inplace_lub(LE(LE.L_MAY_HAVE))
                        
                        if not son_common and not parent_common:
                            # both endpoints are not common, so this edge will be added when the vertices will be added
                            pass
                        elif not son_common:
                            # only parent in graph. add son
                            if self.vertices[e.parent].sons.has_key(e.label):
                                self.unlink_single_son(e.parent, e.label)
                            self.vertices[e.parent].sons[e.label] = e
                        else:
                            # only son in graph. add parent
                            self.vertices[son].all_parents.add_element(e.label, e.parent)
    
    def _modify_existent_vertices(self, common_vertices, other):
        """
        vertices and edges that are in self graph and not in other's, should be modified
        """
        for v in self.vertices.keys():
            # go over all edges of self graph, and if they are not common, lub their knowledge with L_MAY_HAVE
            for ee in self.vertices[v].all_parents.values():
                for e in ee:
                    edge_is_new = True
                    # check if this edge exists in other graph
                    # the two endpoints should exists, and there should be a label connecting them
                    if e.son in common_vertices and e.parent in common_vertices:
                        if other.vertices[e.parent].sons.has_key(e.label):
                            if other.vertices[e.parent].sons[e.label].son != e.son:
                                assert False
                            edge_is_new = False
                            
                    if edge_is_new:
                        e.knowledge.inplace_lub(LE(LE.L_MAY_HAVE))
    
    def lub(self, other):
        """
        performs lub between self and other
        pairs are pairs of vertices that should be equal
        self_inds are vertices that exists only in self
        other_inds are vertices that exists only in other
        """
        vertices_pairs = set()
        common_edges = set()
        common_vertices = set()
        
        # rename constants of other
        self._merge_cons(other)
        
        # find the intersection of both graphs
        self._find_common_vertices_and_edges(other, common_vertices, common_edges, vertices_pairs)
        
        # lub pairs of equal vertices
        for (y, x) in vertices_pairs:
            self.vertex_lub(x, other, y)
        
        # perform lub between the common edges
        self._handle_common_edges(common_edges)
        
        # rename equal vertices of other graph
        other.rename_vertices_indices(dict(vertices_pairs))
        
        # add other graph vertices and edges to self graph
        self._add_other_graph(other, common_vertices)
        
        # modify self graph
        self._modify_existent_vertices(common_vertices, other)
    
    def fill_graphs(self, other):
        """
        if a vertex exists in both graphs, but explicitly in one and implicitly
        in the other, we want to make sure that the vertex exists explicitly in
        both graphs.
        a vertex can exist implicitly if it can be a son due to constant, or
        due to TOP of its father
        """
        
        q = deque([(0, 0)])
        # go over the whole graph to find common vertices and edges
        while len(q):
            (x, y) = q.popleft()
            x_sons = set(self.vertices[x].sons.keys())
            y_sons = set(other.vertices[y].sons.keys())
            
            # go over all sons of x which are not exists in y yet
            for only_x in x_sons.difference(y_sons):
                father_ind = y
                basename = self.vertices[x].sons[only_x].label
                can_have = other.can_have_son(father_ind, basename)
                
                # check if the son should be exist as a son of y
                if can_have == 'top' or can_have == 'const':
                    var_ind = other.create_new_vertex(father_ind, basename)
                    if can_have == 'top':
                        other.set_top(var_ind)
                    elif can_have == 'const':    
                        other.propagate_const_to_son(father_ind, basename)
                    
                    q.append((self.vertices[x].sons[only_x].son, var_ind))
            
            # do the same, but for the opposite graphs role
            for only_y in y_sons.difference(x_sons):
                father_ind = x
                basename = other.vertices[y].sons[only_y].label
                can_have = self.can_have_son(father_ind, basename)
                
                if can_have == 'top' or can_have == 'const':
                    var_ind = self.create_new_vertex(father_ind, basename)
                    if can_have == 'top':
                        self.set_top(var_ind)
                    elif can_have == 'const':    
                        self.propagate_const_to_son(father_ind, basename)
                    
                    q.append((var_ind, other.vertices[y].sons[only_y].son))

            common = x_sons.intersection(y_sons)
            for c in common:
                s0 = self.vertices[x].sons[c].son
                s1 = other.vertices[y].sons[c].son
                if s0 != 0 and s1 != 0:
                    q.append((s0, s1))
        