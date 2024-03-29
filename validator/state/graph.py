import copy
from collections import deque
import itertools

from lattice import LatticeElement as LE
from utils import is_primitive, is_callable, TopFunction, IntFunction, is_top_func, \
    INT_FUNCS, BOOL_FUNCS

class SonKnowledge(object):
    FALSE = -1
    TOP = 0
    CONST = 1
    MAYBE_CONST = 2
    EDGE = 3


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
    def __init__(self, label=None, son=None, par=0, know=None):
        self.label = label
        self.son = son
        self.parent = par
        self.knowledge = copy.copy(know) if know is not None else LE(LE.L_MUST_HAVE)

    def __repr__(self):
        return '(%d)->(%d)\tlabel\t%s\tknowledge\t%s' \
               % (self.son, self.parent, self.label, self.knowledge)


class GraphVertex(object):
    def __init__(self):
        self.all_constants = set()
        self.mutable = LE(LE.L_BOTOM)  # default is to don't know about mutability
        self.callable = LE(
            LE.L_BOTOM)  # default is to don't know about callability, but caller must know this (logically, default is to be not-callable)
        self.sons = dict()
        self.all_parents = SetDict()
        self.knowledge = LE(LE.L_MUST_HAVE)
        self.metadata = set()

    def remove_parent(self, lbl, edge):
        self.all_parents[lbl].remove(edge)
        if not self.all_parents[lbl]:
            self.all_parents.pop(lbl)

    def remove_son(self, lbl, edge):
        self.sons.pop(lbl)

    def __repr__(self):
        return 'knowledge\t%s\tmutable\t%s\n' % (self.knowledge, self.mutable) + \
               'all constants:\t%s\n' % self.all_constants + \
               'sons:\n%s\n' % ('\n'.join(['\t%s' % x for x in self.sons.values()])) + \
               'parents:\n%s\n' % ('\n'.join(['\t%s' % x for x in self.all_parents.values()])) + \
               'metadata possibilities:\t%d\tcallable:\t%s\n' % (len(self.metadata), self.callable)


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
        v in self.vertices.values() => v.bio_edge.par >= 0 | v.constant >= 0 | v.is_top (this should be maintained by
        caller)
        the graph is a DAG
    """

    def __init__(self):
        self.next_ind = 0
        self.vertices = dict()

        self.next_cons = 0
        self.types_dict = dict()
        self.all_cons = dict()

        self.create_new_vertex(label='')

    def set_vertex_to_const(self, vertex_ind, const):
        """
        set a vertex to be a constant
        add the constant to the constants pull if necessary (a constant of a new type)
        mark this vertex as non top
        """
        self.vertices[vertex_ind].all_constants.clear()
        self.vertices[vertex_ind].mutable = LE(LE.L_BOTOM)
        self.vertices[vertex_ind].callable = LE(LE.L_MUST_NOT_HAVE)
        self.vertices[vertex_ind].metadata.clear()

        self._add_const_to_vertex(vertex_ind, const)

    def _add_const_to_vertex(self, vertex_ind, const):
        """
        add possible const to vertex
        mark the vertex as non TOP
        """
        t = type(const)
        cons_ind = self.types_dict.get(t, -1)
        if cons_ind < 0:
            cons_ind = self.next_cons
            self.next_cons += 1
            self.types_dict[t] = cons_ind
            self.all_cons[cons_ind] = const

        self.vertices[vertex_ind].all_constants.add(cons_ind)
        # new var won't be top
        self.vertices[vertex_ind].knowledge = LE(LE.L_MUST_HAVE)

        # update mutability of vertex, based on the constant
        primitive = is_primitive(const)
        if primitive:
            self.vertices[vertex_ind].mutable.inplace_lub(LE(LE.L_MUST_NOT_HAVE))
        else:
            self.vertices[vertex_ind].mutable.inplace_lub(LE(LE.L_MUST_HAVE))

        # update callability, bases on the constant    
        is_function = is_callable(const)
        if is_function:
            self.vertices[vertex_ind].callable.inplace_lub(LE(LE.L_MUST_HAVE))
        else:
            self.vertices[vertex_ind].callable.inplace_lub(LE(LE.L_MUST_NOT_HAVE))

    def create_new_vertex(self, parent=0, label=''):
        """
        add new vertex to the graph, returns the new vertex index
        initialize the vertex with a label. no father, no constant, not TOP
        """
        v_ind = self.next_ind
        self.next_ind += 1
        new_v = GraphVertex()
        self.vertices[v_ind] = new_v

        self.make_parent(v_ind, parent, label)

        return v_ind

    def make_parent(self, son, par, label, know=None):
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

    def set_callable(self, v):
        """
        set vertex v to be callable
        """
        self.vertices[v].callable = LE(LE.L_MUST_HAVE)

    def get_callable(self, v):
        """
        get callability of a vertex
        returns an element from the lattice
        """
        return self.vertices[v].callable

    def set_mutable(self, v):
        """
        set vertex v to be mutable
        """
        self.vertices[v].mutable = LE(LE.L_MUST_HAVE)

    def get_mutable(self, v):
        """
        get mutability of a vertex
        returns an element from the lattice
        """
        return self.vertices[v].mutable

    def set_top(self, v):
        """
        set a var to be TOP
        set its constant to be -1
        clear metadata (?)
        """
        self._vertex_set_top(self.vertices[v])

    @staticmethod
    def _vertex_set_top(vertex):
        vertex.knowledge.val = LE.L_TOP
        vertex.all_constants.clear()
        vertex.mutable = LE(LE.L_BOTOM)
        vertex.callable = LE(LE.L_TOP)
        vertex.metadata.clear()
        vertex.metadata.add(TopFunction.get(2))
        # do we want to mark all its sons edges to L_MAY_HAVE? currently not, becuase
        # this function is called only on new vertices, and on vertices that are lubbed,
        # so the edges handling is done by someone else. but we need to reconsider this

    def set_botom(self, v):
        """
        set a var to be BOTOM
        our purpose is that it won't affect any vertex u for which we 
        will perform lub(u,v) (=u)
        """
        self.vertices[v].knowledge.val = LE.L_BOTOM
        self.vertices[v].all_constants.clear()
        self.vertices[v].mutable = LE(LE.L_BOTOM)
        self.vertices[v].callable = LE(LE.L_BOTOM)
        self.vertices[v].metadata.clear()

    def is_botom(self, v):
        """
        is a var BOTOM?
        """
        return self.vertices[v].knowledge.val == LE.L_BOTOM

    def _get_vertex_consts(self, vertex_ind):
        """
        received a vertex index
        return the constant which this vertex correspond to, or MyNone if there
        is no such constant
        """
        vertex_consts = set([self.all_cons.get(cons_ind) \
                             for cons_ind in self.vertices[vertex_ind].all_constants])

        return vertex_consts

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
        else:
            assert False

    def propagate_const_to_son(self, vertex_ind, son_label):
        """
        when vertex_ind is equal to a constant, and we want its son labelled son_label
        to have a constant too
        """
        # get all possible constants of father
        possible_consts = self._get_vertex_consts(vertex_ind)
        if len(possible_consts) == 0:
            return

        son_ind = self.vertices[vertex_ind].sons[son_label].son

        maybe_edge = False

        for c in possible_consts:
            try:
                # add possible constant to son
                son_const = c.__getattribute__(son_label)
                self._add_const_to_vertex(son_ind, son_const)
                if is_callable(son_const):
                    # add metadata function to son
                    if (type(c), son_label) in INT_FUNCS:
                        self.vertices[son_ind].metadata.add(IntFunction.get(2))
                        self._consolidate_metadata(self.vertices[son_ind])
                    elif (type(c), son_label) in BOOL_FUNCS:
                        # self.vertices[son_ind].metadata.add(BoolFunction.get(1))
                        self.vertices[son_ind].metadata.add(IntFunction.get(2))
                        self._consolidate_metadata(self.vertices[son_ind])
                    else:
                        self.vertices[son_ind].metadata.add(
                            TopFunction.get(30))  # maximum of 30 arguments
                        self._consolidate_metadata(self.vertices[son_ind])

            except:
                # there exists a constant for father, for which the label is illegal
                maybe_edge = True
                pass

        if maybe_edge:
            # if there is a father constant for which the son cannot be labelled due
            # to constant, we mark this edge as L_MAY_HAVE
            self.vertices[vertex_ind].sons[son_label].knowledge.inplace_lub(LE(LE.L_MAY_HAVE))

    def can_have_son(self, vertex_ind, son_label):
        """
        returns True if the son can be legally added to a vertex
        the returned value can be 'edge', 'top' or 'const', depending on
        the way we know the son can exists
        """
        if self.vertices[vertex_ind].sons.has_key(son_label):
            return SonKnowledge.EDGE

        if self.is_top(vertex_ind):
            return SonKnowledge.TOP

        vertex_consts = self._get_vertex_consts(vertex_ind)
        if len(vertex_consts) == 0:
            return SonKnowledge.FALSE

        # check for how many possible constants the label can belong
        success = 0
        failed = 0
        for c in vertex_consts:
            try:
                son_const = c.__getattribute__(son_label)
                success += 1
            except:
                failed += 1

            if success > 0 and failed > 0:
                break

        # if there is no constant that this label can belongs to
        if success == 0:
            return SonKnowledge.FALSE
        elif failed == 0:
            # this implies success > 0
            return SonKnowledge.CONST
        else:
            # success > 0 and failed > 0
            return SonKnowledge.MAYBE_CONST

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

    def is_single_son(self, ind):
        """
        returns True if this vertex has only a single parent
        """
        return len(self.vertices[ind].all_parents) == 1 and \
               len(self.vertices[ind].all_parents.values()[0]) == 1

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
            title = '%d' % ind
            sides_len = 50 - len(title) - 2
            title = '%s %d %s' % ('-' * (sides_len / 2), ind, '-' * (sides_len - sides_len / 2))
            res += '%s\n%s\n' % (title, ver)

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
            used_constant.update(ver.all_constants)

        for t, i in self.types_dict.items():
            if i not in used_constant:
                self.types_dict.pop(t)

        for i in self.all_cons.keys():
            if i not in used_constant:
                self.all_cons.pop(i)

        # compress constant indices
        c_mapping = dict(zip(sorted(self.all_cons.keys()), range(len(self.all_cons))))
        self.rename_constants_indices(c_mapping)
        self.next_cons = max(self.all_cons.keys() + [-1]) + 1

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
                new_v = mapping.get(v, v)
                if not new_vertices.has_key(new_v):
                    new_vertices[new_v] = gv
                else:
                    existing_v = new_vertices[new_v]
                    self._vertex_obj_lub(existing_v, gv)

                    # merge sons
                    e_sons = set(existing_v.sons.keys())
                    g_sons = set(gv.sons.keys())

                    common = e_sons.intersection(g_sons)
                    for g_lbl, g_edge in gv.sons.items():
                        if g_lbl not in common:
                            existing_v.sons[g_lbl] = g_edge
                        else:
                            self._handle_common_edges([(existing_v.sons[g_lbl], g_edge)])

                    # merge parents
                    e_pars = set(existing_v.all_parents.keys())
                    g_pars = set(gv.all_parents.keys())

                    common = e_pars.intersection(g_pars)
                    for g_lbl, g_set in gv.all_parents.items():
                        if g_lbl not in common:
                            existing_v.all_parents[g_lbl] = g_set
                        else:
                            e_set = existing_v.all_parents[g_lbl]
                            e_ind_to_edge = dict()
                            for e in e_set:
                                e_ind_to_edge[e.parent] = e

                            for gp in g_set:
                                if not e_ind_to_edge.has_key(gp.parent):
                                    e_set.add(gp)
                                else:
                                    self._handle_common_edges([(e_ind_to_edge[gp.parent], gp)])

        self.vertices = new_vertices
        self.next_ind = max(self.vertices.keys()) + 1

    def rename_constants_indices(self, mapping):
        """
        rename each constant index:
            x <- mapping[x]
        """
        for v in self.vertices.keys():
            new_cons_set = set()
            for c in self.vertices[v].all_constants:
                new_cons_set.add(mapping.get(c, c))

            self.vertices[v].all_constants = new_cons_set

        new_all_cons = dict()
        for c in self.all_cons.keys():
            cv = self.all_cons.pop(c)
            new_all_cons[mapping.get(c, c)] = cv
        self.all_cons = new_all_cons

        for t in self.types_dict.keys():
            self.types_dict[t] = mapping.get(self.types_dict[t], self.types_dict[t])

        self.next_cons = max(self.all_cons.keys() + [-1]) + 1

    def rename_constants_offset(self, offset):
        """
        rename each constant index:
            x <- x + offset
        """
        mapping = dict([(x, x + offset) for x in self.all_cons.keys()])
        self.rename_constants_indices(mapping)

    @staticmethod
    def _consolidate_metadata(vertex):
        """
        if the vertex (not index) has many TOP functions, remove all but one
        """
        to_remove = set()
        is_first_top = True
        was = set()
        for m in vertex.metadata:
            if (m.name, m.lineno) in was:
                to_remove.add(m)
                continue
            else:
                was.add((m.name, m.lineno))

            if is_top_func(m):
                if is_first_top:
                    is_first_top = False
                else:
                    to_remove.add(m)

        vertex.metadata.difference_update(to_remove)

    def vertex_lub(self, x, other, y):
        """
        lub between self.vertices[x] and other.vertices[y]
        """
        v0 = self.vertices[x]
        v1 = other.vertices[y]

        self._vertex_obj_lub(v0, v1)

    @staticmethod
    def _vertex_obj_lub(v0, v1):
        v0.knowledge.inplace_lub(v1.knowledge)

        if v0.knowledge.val == LE.L_TOP or v1.knowledge.val == LE.L_TOP:
            # if one of the vertices is TOP, so will be their lub
            # the following line also clears all_constants and mutability
            Graph._vertex_set_top(v0)
        else:
            # otherwise, just merge their possible constants and metadata
            v0.all_constants.update(v1.all_constants)
            v0.mutable.inplace_lub(v1.mutable)
            v0.callable.inplace_lub(v1.callable)
            v0.metadata.update(v1.metadata)
            Graph._consolidate_metadata(v0)

    @staticmethod
    def _handle_common_edges(edge_pairs):
        """
        lub between any two edges
        first element is edge of self, second element is edge of other
        """
        for (e0, e1) in edge_pairs:
            e0.knowledge.inplace_lub(e1.knowledge)

    def _merge_vertices(self, h):
        """
        merge all vertices in h, where h is a set of tuples, each tuple is a 
        set of equal vertices which needs to be merged
        """
        for m in h:
            u0 = m[0]
            for v in m[1:]:
                self.vertex_lub(u0, self, v)

                # merge parents
                for lbl, v_parents in self.vertices[v].all_parents.items():

                    if not self.vertices[u0].all_parents.has_key(lbl):
                        u0_parents = set()
                    else:
                        u0_parents = set([x.parent for x in self.vertices[u0].all_parents[lbl]])

                    for e in v_parents:
                        if e.parent in u0_parents:
                            # e.parent has two sons with the same label
                            assert False
                        else:
                            e.son = u0
                            self.vertices[u0].all_parents.add_element(lbl, e)

                only_u0_sons = set(self.vertices[u0].sons.keys()).difference(set(self.vertices[v].sons.keys()))
                # merge sons
                for lbl, e_v in self.vertices[v].sons.items():

                    if self.vertices[u0].sons.has_key(lbl):
                        # remove unnecessary edge from son
                        self.vertices[e_v.son].remove_parent(lbl, e_v)

                        e_u0 = self.vertices[u0].sons[lbl]
                        # found common son, lub the knowledge of the edge
                        e_u0.knowledge.inplace_lub(e_v.knowledge)
                        # and lub the vertex
                        self.vertex_lub(e_u0.son, self, e_v.son)
                    else:
                        # add son to u0
                        e_v.parent = u0
                        self.vertices[u0].sons[lbl] = e_v
                        # new edge
                        e_v.knowledge.inplace_lub(LE(LE.L_MAY_HAVE))

                # another new edges
                for lbl in only_u0_sons:
                    self.vertices[u0].sons[lbl].knowledge.inplace_lub(LE(LE.L_MAY_HAVE))

                # clear pointers to edges
                self.vertices[v].sons.clear()
                self.vertices[v].all_parents.clear()

    def _find_common_vertices_and_edges(self, other, common_vertices, common_edges, vertices_pairs, \
                                        self_merged, other_merged):
        """
        result:
            common_vertices: common vertices between self graph and other graph
            common_edges: common edges between self graph and other graph
            vertices_pairs: pairs (y,x) of vertices in cartesian(other.vertices.keys(), self.vertices.keys())
                            which are the same vertices
            self_merged: a dictionary from vertex index to all other indices it was merged with (only concerning self
            graph)
            other_merged: like self_merged but for other
        this function also merges vertices if needed
        """
        common_vertices.add(0)
        vertices_pairs_help = set()

        was = set()
        q = deque([(0, 0)])
        # go over the whole graph to find common vertices and edges
        while len(q):
            (x, y) = q.popleft()
            vertices_pairs_help.add((y, x))
            common = set(self.vertices[x].sons.keys()).intersection(other.vertices[y].sons.keys())
            for c in common:
                e0 = self.vertices[x].sons[c]
                e1 = other.vertices[y].sons[c]
                common_edges.add((e0, e1))
                s0 = e0.son
                s1 = e1.son
                if s0 != 0 and s1 != 0:
                    if not (s0, s1) in was:
                        q.append((s0, s1))
                        common_vertices.add(s0)
                        common_vertices.add(s1)
                        was.add((s0, s1))

        # find vertices that needs to be merged
        d0 = dict()
        d1 = dict()
        for (y, x) in vertices_pairs_help:
            d0[y] = d0.get(y, []) + [x]
            d1[x] = d1.get(x, []) + [y]

        presentors = dict()
        h0 = set()
        for y0 in d0.keys():
            if len(d0[y0]) > 1:
                h0.add(tuple(d0[y0]))
                pres = tuple(d0[y0])[0]
                for a in tuple(d0[y0])[1:]:
                    presentors[a] = pres

        was_y = set()
        for (y, x) in vertices_pairs_help:
            if y not in was_y:
                vertices_pairs.add((y, presentors.get(x, x)))
            was_y.add(y)

        h1 = set()
        for x0 in d1.keys():
            if len(d1[x0]) > 1:
                h1.add(tuple(d1[x0]))

        # merge all self vertices that appears in h0, and all other's vertices
        # that appears in h1. merge should contain:
        # * vertex_lub
        # * renaming name of some vertex
        # * merge of all_parents. mutual parents (with respect to edge label) cannot exist
        # * merge of all sons. if mutual sons exists- lub the knowledge of the edges, and
        # lub the vertices

        self._merge_vertices(h0)
        other._merge_vertices(h1)

        for tup in h0:
            for (u, v) in itertools.combinations(tup, 2):
                self_merged[u] = self_merged.get(u, []) + [v]
                self_merged[v] = self_merged.get(v, []) + [u]
        for tup in h1:
            for (u, v) in itertools.combinations(tup, 2):
                other_merged[u] = other_merged.get(u, []) + [v]
                other_merged[v] = other_merged.get(v, []) + [u]

        self_clos = self._transitive_closure(self_merged)
        for v in self_merged.keys():
            self_merged[v] = self_clos[v]

        other_clos = self._transitive_closure(other_merged)
        for v in other_merged.keys():
            other_merged[v] = other_clos[v]

    @staticmethod
    def _transitive_closure(d):
        """
        transitive closure of a mapping using BFS
        """
        res = dict()
        waiting = deque(d.keys())
        was = set()
        while len(waiting):
            u = waiting.popleft()
            if u in was:
                continue

            q = deque()
            s = set()
            q.append(u)
            was.add(u)
            while len(q) > 0:
                u = q.popleft()
                s.add(u)
                for v in d[u]:
                    if v in was:
                        continue
                    q.append(v)
                    was.add(v)

            for v in s:
                res[v] = set(s)

        return res

    def _merge_cons(self, other):
        """
        merge constant indices between self and other, if the constant are of the same type
        modifies other's constants
        adds other constants to self
        """
        cons_pairs = []
        for t, i in self.types_dict.items():
            other_ind = other.types_dict.get(t, -1)
            if other_ind >= 0:
                cons_pairs.append((other_ind, i))

        other.rename_constants_indices(dict(cons_pairs))

        # add other consts to self
        known_consts = set(self.all_cons.keys())

        for t, i in other.types_dict.items():
            if i not in known_consts:
                self.types_dict[t] = i

        for i, c in other.all_cons.items():
            if i not in known_consts:
                self.all_cons[i] = c

        # constants were added
        self.next_cons = max(self.all_cons.keys() + [-1]) + 1

    def _add_other_graph(self, other, common_vertices, self_merged):
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
                            s1 = self.vertices[e.parent].sons[e.label].son
                            s2 = e.son
                            if s1 != s2 and s2 not in self_merged.get(s1, []):
                                print 'assert false because %d != %d' % (s1, s2)
                                print 'but self_merged[%d] = %s' % (s2, self_merged[s2])
                                print 'but self_merged[%d] = %s' % (s1, self_merged[s1])
                                print 'self_merged', self_merged
                                print 'problematic edge'
                                print e
                                print 'self parent'
                                print self.vertices[e.parent]
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

        # vertices were added
        self.next_ind = max(self.vertices.keys()) + 1

    def _modify_existent_vertices(self, common_vertices, other, other_merged):
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
                            s1 = other.vertices[e.parent].sons[e.label].son
                            s2 = e.son
                            if s1 != s2 and s2 not in other_merged.get(s1, []):
                                print 'problematic edge'
                                print e
                                print '%d != %d' % (s1, s2)
                                print 'other_merged %s' % other_merged
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
        self_merged = dict()
        other_merged = dict()

        # rename constants of other
        self._merge_cons(other)

        # find the intersection of both graphs
        self._find_common_vertices_and_edges(other, common_vertices, common_edges, \
                                             vertices_pairs, self_merged, other_merged)

        # lub pairs of equal vertices
        for (y, x) in vertices_pairs:
            self.vertex_lub(x, other, y)

        # perform lub between the common edges
        self._handle_common_edges(common_edges)

        mapping_dict = dict(vertices_pairs)

        # rename equal vertices of other graph
        other.rename_vertices_indices(mapping_dict)

        # rename merged vertices of other
        other_merged = self.rename_dict(mapping_dict, other_merged)

        # add other graph vertices and edges to self graph
        self._add_other_graph(other, common_vertices, self_merged)

        # modify self graph
        self._modify_existent_vertices(common_vertices, other, other_merged)

    @staticmethod
    def rename_dict(mapping, dict_to_rename):
        """
        """
        res = dict()
        for k, v in dict_to_rename.items():
            src = mapping.get(k, k)
            dst = res.get(src, []) + [mapping.get(x, x) for x in v]
            res[src] = list(set(dst))

        return res

    def fill_graphs(self, other):
        """
        if a vertex exists in both graphs, but explicitly in one and implicitly
        in the other, we want to make sure that the vertex exists explicitly in
        both graphs.
        a vertex can exist implicitly if it can be a son due to constant, or
        due to TOP of its father
        """

        was = set()
        q = deque([(0, 0, 0)])
        # go over the whole graph to find common vertices and edges
        while len(q):
            (x, y, depth) = q.popleft()
            # limit depth
            if depth > 10:
                continue
            x_sons = set(self.vertices[x].sons.keys())
            y_sons = set(other.vertices[y].sons.keys())

            # go over all sons of x which are not exists in y yet
            for only_x in x_sons.difference(y_sons):
                father_ind = y
                basename = self.vertices[x].sons[only_x].label
                can_have = other.can_have_son(father_ind, basename)

                # check if the son should be exist as a son of y
                if can_have == SonKnowledge.TOP or can_have == SonKnowledge.CONST or can_have == SonKnowledge.MAYBE_CONST:
                    var_ind = other.create_new_vertex(father_ind, basename)
                    if can_have == SonKnowledge.TOP:
                        other.set_top(var_ind)
                    elif can_have == SonKnowledge.CONST or can_have == SonKnowledge.MAYBE_CONST:
                        other.propagate_const_to_son(father_ind, basename)

                    to_add = (self.vertices[x].sons[only_x].son, var_ind, depth + 1)
                    if to_add[:2] not in was:
                        q.append(to_add)
                        was.add(to_add[:2])

            # do the same, but for the opposite graphs role
            for only_y in y_sons.difference(x_sons):
                father_ind = x
                basename = other.vertices[y].sons[only_y].label
                can_have = self.can_have_son(father_ind, basename)

                if can_have == SonKnowledge.TOP or can_have == SonKnowledge.CONST or can_have == SonKnowledge.MAYBE_CONST:
                    var_ind = self.create_new_vertex(father_ind, basename)
                    if can_have == SonKnowledge.TOP:
                        self.set_top(var_ind)
                    elif can_have == SonKnowledge.CONST or can_have == SonKnowledge.MAYBE_CONST:
                        self.propagate_const_to_son(father_ind, basename)

                    to_add = (var_ind, other.vertices[y].sons[only_y].son, depth + 1)
                    if to_add[:2] not in was:
                        q.append(to_add)
                        was.add(to_add[:2])

            common = x_sons.intersection(y_sons)
            for c in common:
                s0 = self.vertices[x].sons[c].son
                s1 = other.vertices[y].sons[c].son
                if s0 != 0 and s1 != 0:
                    to_add = (s0, s1, depth + 1)
                    if to_add[:2] not in was:
                        q.append(to_add)
                        was.add(to_add[:2])

    def get_main_vars(self):
        """
        returns a list of the main variables
        this is simply the labels on the sons of root vertex
        """
        res = []
        for edge in self.vertices[0].sons.values():
            if edge.son != 0:
                res.append(edge.label)
        return res

    def add_graph(self, other):
        """
        add other graph to self, after self graph is already prepared for it
        """
        # rename constants of other
        self._merge_cons(other)

        # merge root vertex. we already cleaned up self root vertex
        for (lbl, edge) in other.vertices[0].sons.items():
            self.vertices[0].sons[lbl] = edge

        # add other vertices
        for v in other.vertices.keys():
            if v != 0:
                self.vertices[v] = other.vertices[v]

        # vertices were added
        self.next_ind = max(self.vertices.keys()) + 1

    def add_metadata(self, vertex_ind, metadata):
        """
        add metadata to a vertex
        """
        self.vertices[vertex_ind].metadata = set([metadata])

    def get_metadata(self, vertex_ind):
        """
        receive vertex metadata
        """
        return self.vertices[vertex_ind].metadata

    def clone(self):
        """
        returns a copy of the graph. constants won't be copied
        """
        res = Graph()
        res.next_ind = self.next_ind
        res.next_cons = self.next_cons
        for t, i in self.types_dict.items():
            res.types_dict[t] = i
        for i, c in self.all_cons.items():
            res.all_cons[i] = c
        res.vertices = copy.deepcopy(self.vertices)

        return res