import logging
from collections import deque
from lattice import LatticeElement as LE
logging.basicConfig(level = logging.DEBUG)

"""
TODO
(maybe) need to solve the problem where a constant refers to itself
need to understand what the knowledge field actually means
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
        self.knowledge = know if know is not None else LE(LE.L_MUST_HAVE)
    
    def __repr__(self):
        return '(%d)->(%d)\tlabel\t%s\tknowledge\t%s' \
               %(self.son, self.parent, self.label, self.knowledge)

class GraphVertex(object):
    def __init__(self, ind, label, bio_parent):
        self.ind = ind
        self.constant = -1
        self.bio_edge = GraphEdge(label, son = ind, par = bio_parent)
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
    
    def create_new_vertex(self, bio_parent = 0, label = ''):
        """
        add new vertex to the graph, returns the new vertex index
        initialize the vertex with a label. no father, no constant, not TOP
        """
        v_ind = self.next_ind
        self.next_ind += 1
        new_v = GraphVertex(v_ind, label, bio_parent)
        self.vertices[v_ind] = new_v
        
        bedge = new_v.bio_edge
        self.vertices[v_ind].all_parents.add_element(label, bedge)
        if self.vertices[bio_parent].sons.has_key(label):
            self.unlink_single_son(bio_parent, label)
        self.vertices[bio_parent].sons[label] = bedge
        
        return v_ind
    
    def make_step_parent(self, son, par, label):
        """
        this function refers to step parent (not biological)
        connect son and parent by an edge (directed from the son to the parent)
        """
        if not self.vertices.has_key(son) or not self.vertices.has_key(par):
            raise KeyError()
        
        new_edge = GraphEdge(label, son, par)
        self.vertices[son].all_parents.add_element(label, new_edge)
        
        if self.vertices[par].sons.has_key(label):
            self.unlink_single_son(par, label)
        self.vertices[par].sons[label] = new_edge
    
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
        # TODO do we want to mark all its sons edges to TOP?
    
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

        while cur_v != 0:
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
            except Exception:
                logging.debug('[_get_rooted_const] failed to get attribute %s \
                                   from type %s' %(att, type(root_const)))
                return None
        
        return root_const
    
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
        raise Exception("called get_son_knowledge for nonexistent son. parent %d label %s" %(par, lbl))
    
    def propagate_const_to_son(self, vertex_ind, son_label):
        cons_ind = self.vertices[vertex_ind].constant
        son_ind = self.vertices[vertex_ind].sons[son_label]
        
        if cons_ind < 0:
            return
        
        if son_ind < 0:
            return
            
        vertex_const = self.all_cons[cons_ind]
        
        try:
            son_const = vertex_const.__getattribute__(son_label)
        except Exception:
            return
        
        self.set_vertex_to_const(vertex_const, son_const)
    
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
        if vertex_const is None:
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
        vertex_const = self._get_rooted_const(vertex_ind)
        
        for lbl in self.vertices[vertex_ind].sons.keys():
            self.unlink_single_son(vertex_ind, lbl)
        
        return
    
    def unlink_single_son(self, vertex_ind, son_label):
        """
        propagate constant from father to single son
        """
        if not self.vertices[vertex_ind].sons.has_key(son_label):
            return
        
        vertex_const = self._get_rooted_const(vertex_ind)
        
        edge = self.vertices[vertex_ind].sons[son_label]
        v = edge.son
        lbl = son_label
        # remove from all_parents
        self.vertices[v].remove_parent(lbl, edge)
        
        if self.vertices[v].bio_edge.parent != vertex_ind:
            # vertex belongs to another parent
            pass
        else:
            # bio parent is -1 means that there is no bio parent
            self.vertices[v].bio_edge.parent = -1
            self.vertices[v].bio_edge.label = None # just to be sure, doesn't really matter
            
            if self.vertices[v].constant < 0:
                need_to_set_top = True
                if vertex_const is not None:
                    try:
                        new_const = vertex_const.__getattribute__(lbl)
                        self.set_vertex_to_const(v, new_const)
                        need_to_set_top = False
                    except Exception:
                        logging.debug('[unlink_single_son] failed to get \
                                       attribute %s from type %s' \
                                       %(lbl, type(new_const)))
                        
                if need_to_set_top:
                    # we set to top in any case we were not able
                    # to determine the constant for this vertex
                    # this is because we can know nothing about the sons of this
                    # vertex, except if they are already exists
                    self.set_top(v)
        
        # by this point, parent of son is -1, and is TOP or
        # has a non negative constant index
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

    def _propagate_constant_to_vertex(self, v):
        """
        call this when you need to explicitly know what is the constant of
        some vertex
        """
        # TODO CONTINUE FROM HERE
        
        chain_to_const = []
            
        u = v
        bedge = self.vertices[u].bio_edge
        
        while bedge.parent >= 0 and self.vertices[u].constant < 0:
            unused_chain.append((bedge.parent, bedge.label))
            u = bedge.parent
            bedge = self.vertices[u].bio_edge
            
        if self.vertices[u].constant >= 0:
            # u != v
            for (vertex, lbl) in unused_chain[::-1]:
                self.unlink_single_son(vertex, lbl)
        # TODO CONTINUE FROM HERE
        
    def collect_garbage(self):
        """
        remove unused vertices from the graph
        a vertex is in use if there is a path from it to the root vertex, or if it is a biological parent
        of any vertex which is in use
        also calls to compress indices to decrease vertices indices as can
        """
        used_vertices = set()
        q = deque([0])
        
        while len(q):
            v = q.popleft()
            neis = [edge.son for edge in self.vertices[v].sons.values()]
            # bio_parent = self.vertices[v].bio_edge.parent
            # if bio_parent >= 0:
            #     neis.append(bio_parent)
                
            for u in neis:
                if u not in used_vertices:
                    used_vertices.add(u)
                    q.append(u)
        
        for v in self.vertices.keys():
            if self.vertices[v].constant >= 0:
                continue
        
            # we need to check if we need to propagate constant from unused vertices to used vertices
            unused_chain = []
            
            u = v
            bedge = self.vertices[u].bio_edge

            if bedge.parent in used_vertices:
                # biological father should exist even after garbage will be collected
                continue
            
            while bedge.parent >= 0 and self.vertices[u].constant < 0:
                unused_chain.append((bedge.parent, bedge.label))
                u = bedge.parent
                bedge = self.vertices[u].bio_edge
                
            if self.vertices[u].constant >= 0:
                # u != v
                for (vertex, lbl) in unused_chain[::-1]:
                    self.unlink_single_son(vertex, lbl)
        
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
        
        for t, i in self.types_dict.values():
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
        self.rename_vertices_indices(self.build_compressed_mapping())
        self.next_ind = max(self.vertices.keys()) + 1
    
    def rename_vertices_offset(self, offset):
        """
        rename each vertex index:
            x <- x + offset
        root vertex remain to be index 0
        """
        mapping = dict([(x, x + offset) for x in self.vertices.values()])
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
            if v == 0:
                continue
            gv = self.vertices.pop(v)
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
        mapping = dict([(x, x + offset) for x in self.all_cons.values()])
        self.rename_constants_indices(mapping)
    
    def vertex_lub(x, other, y):
        """
        lub between self.vertices[x] and other.vertices[y]
        """
        v0 = self.vertices[x]
        v1 = other.vertices[y]
        
        v0.knowledge.inplace_lub(v1.knowledge)
        
        if v0.constant != v1.constant:
            # TODO make a set of all possible constants
            v0.constant = -1
        
        # TODO continue to write this function
        
    
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
            vertices_pairs.add((x, y))
            common = set(self.vertices[y].sons.keys()).intersection(other.vertices[x].sons.keys())
            for c in common:
                e0 = self.vertices[y].sons[c]
                e1 = other.vertices[x].sons[c]
                common_edges.add((e0, e1))
                s0 = e0.son
                s1 = e1.son
                q.append((s0, s1))
                common_vertices.add(s0)
                common_vertices.add(s1)
    
    def _merge_cons(self, other):
        """
        merge constant indices between self and other, if the constant are of the same type
        modifies other's constants
        """
        cons_pairs = []
        for t,i in self.types_dict:
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
                    if e.son in common_vertices and e.parent in common_vertices:
                        pass
                    else:
                        e.knowledge.inplace_lub(LE(LE.L_MAY_HAVE))
    
    def _modify_existent_vertices(self, common_vertices):
        """
        vertices and edges that are in self graph and not in other's, should be modified
        """
        for v in self.vertices.keys():
            # go over all edges of self graph, and if they are not common, lub their knowledge with L_MAY_HAVE
            for ee in self.vertices[v].all_parents.values():
                for e in ee:
                    if e.son in common_vertices and e.parent in common_vertices:
                        pass
                    else:
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
        self._modify_existent_vertices(common_vertices)
        