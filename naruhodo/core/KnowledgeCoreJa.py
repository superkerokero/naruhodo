import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.utils.misc import preprocessText
from naruhodo.backends.cabocha import CaboChunk, CabochaClient
from naruhodo.utils.dicts import MeaninglessDict, SubDict, ObjDict, ObjPostDict, ObjPassiveSubDict, SubPassiveObjDict, NEList, EntityTypeDict, ParallelDict
from naruhodo.core.DependencyCoreJa import DependencyCoreJa

class KnowledgeCoreJa(DependencyCoreJa):
    """Analyze the input text and store the information into a knowledge structure graph(KSG)."""
    def __init__(self, autosub=False):
        """Initialize an analyzer for KSG."""
        self.G = nx.DiGraph()
        self.autosub = autosub
        """
        Graph object of this analyzer.
        It is actually a networkx directed graph object(DiGraph), so you can apply all operations available to DiGraph object using networkx.
        """
        self.entityList = [dict() for x in range(len(NEList))]
        """
        List of entities appeared during this analysis round.
        """
        self.proList = list()
        """
        List of pronouns appeared during this analysis round.
        """
        self.pos = 0
        """
        Current position of the analyzer.
        """
        self.proc = Subprocess('cabocha -f1')
        """
        Communicator to backend for KnowledgeAnalyzer.
        """

    def add(self, inp, pos):
        """Take in a string input and add it to the knowledge structure graph(KSG)."""
        self.pos = pos
        self.para = list()
        # Call backend for dependency parsing.
        cabo = CabochaClient()
        cabo.add(self.proc.query(inp), self.pos)
        pool = [cabo.root]
        plist = [cabo.root]
        self.vlist = dict()
        # Use BFS to get a list of nodes.
        while pool:
            pid = pool.pop(0)
            for cid in cabo.childrenList[pid]:
                pool.append(cid)
                plist.insert(0, cid)
        # Add nodes using plist(from leaves to roots).
        for i in range(len(plist)):
            pid = plist[i]
            self._addChildren(pid, cabo.chunks)
        self._processPara()

        # Return here if self.autosub is False.
        if not self.autosub:
            return
        # If root has no subject, add omitted subject node.
        if self.G.nodes[cabo.chunks[cabo.root].main]['sub'] == '':
            omitted = CaboChunk(-1, cabo.root)
            omitted.main = "省略される主体[{0}@{1}]".format(self.pos, 0)
            omitted.func = "(省略)"
            omitted.type = 0
            omitted.pro = 7
            omitted.surface = "省略される主体"
            omitted.yomi = "ショウリャクサレルシュゴ"
            self._addNode(omitted)
            self._addEdge(omitted.main, cabo.chunks[cabo.root].main, label="(省略)主体", etype="sub")
            self.G.nodes[cabo.chunks[cabo.root].main]['sub'] = omitted.main
        # Add autosub
        for i in range(len(plist)):
            pid = plist[i]
            if cabo.chunks[pid].type in [1, 2] and self.G.nodes[cabo.chunks[pid].main]['sub']== "":
                self._addEdge(self.G.nodes[cabo.chunks[cabo.root].main]['sub'], cabo.chunks[pid].main, label="主体候補", etype="autosub")
                self.G.nodes[cabo.chunks[pid].main]['sub'] = self.G.nodes[cabo.chunks[cabo.root].main]['sub']

    def _addChildren(self, pid, chunks):
        """Add children following rules."""
        if chunks[pid].type in [0, -1]:
            self._addEntity(pid, chunks)
        else:
            self._addPredicate(pid, chunks)

    def _processPara(self):
        """Process parallel words pairs."""
        if self.para:
            for pair in self.para:
                # Add A properties to B
                for key in self.G.successors(pair[0]):
                    if key != pair[1]:
                        self._addEdge(pair[1], key, label=self.G.edges[pair[0], key]['label'], etype=self.G.edges[pair[0], key]['type'])
                for key in self.G.predecessors(pair[0]):
                    if key != pair[1]:
                        self._addEdge(key, pair[1], label=self.G.edges[key, pair[0]]['label'], etype=self.G.edges[key, pair[0]]['type'])
                # Add B properties to A
                for key in self.G.successors(pair[1]):
                    if key != pair[0]:
                        self._addEdge(pair[0], key, label=self.G.edges[pair[1], key]['label'], etype=self.G.edges[pair[1], key]['type'])
                for key in self.G.predecessors(pair[1]):
                    if key != pair[0]:
                        self._addEdge(key, pair[0], label=self.G.edges[key, pair[1]]['label'], etype=self.G.edges[key, pair[1]]['type'])

    def _addEntity(self, pid, chunks):
        """Add parent nodes that are nouns."""
        parent = chunks[pid]
        sub = None
        # Find subject
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.func in SubDict:
                sub = child
                if child.func == "では":
                    if child.negative != 0 or any([val.negative != 0 for key, val in self.G.successors(child.main)]):
                        pass
                    else:
                        sub = None
        if sub:
            self._addNode(parent, sub=sub.main)
            self._addEdge(sub.main, parent.main, label="陳述", etype="stat")
        else:
            self._addNode(parent)
        
        # Lopp through all children
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            # If child is noun
            if child.func in SubDict:
                if child.func == "では":
                    if child.negative != 0 or any([val.negative != 0 for key, val in self.G.successors(child.main)]):
                        pass
                    else:
                        self._addNode(child)
                        self._addEdge(child.main, parent.main, label=child.func, etype="attr")
            elif child.type == 0 and child.func in ["と", "などと"] and child.id + 1 == parent.id and preprocessText(chunks[parent.parent].main) not in ["交代", "交換"]:
                self._addNode(child)
                self._addEdge(child.main, parent.main, label="並列", etype="para")
                self._addEdge(parent.main, child.main, label="並列", etype="para")
                self.para.append([child.main, parent.main])
            elif child.type == 0 and child.func in ParallelDict and child.id + 1 == parent.id:
                self._addNode(child)
                self._addEdge(child.main, parent.main, label="並列", etype="para")
                self._addEdge(parent.main, child.main, label="並列", etype="para")
                self.para.append([child.main, parent.main])
            else:
                self._addNode(child)
                self._addEdge(child.main, parent.main, label=child.func, etype="attr")

    def _addPredicate(self, pid, chunks):
        """Add children following rules."""
        parent = chunks[pid]
        sub = None
        obj = None
        aux = list()
        auxlabel = ""
        # 1st round find absolute subject & object
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            # Process by categories.
            if child.func in SubDict:
                sub = child
            elif child.func in ObjDict:
                obj = child

        # 2nd round find potential subject & object with aux.
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            # Process by categories.
            if child.func in SubDict or child.func in ObjDict:
                continue
            elif child.func in ObjPostDict:
                if not obj and child.type in EntityTypeDict:
                    obj = child
                else:
                    aux.append(child.id)
                    auxlabel += "[{0}]\n".format(child.surface)
            elif child.func in SubPassiveObjDict:
                if parent.passive == 1:
                    if not obj and child.type in EntityTypeDict:
                        obj = child
                    elif not sub and child.type in EntityTypeDict:
                        sub = child
                    else:
                        aux.append(child.id)
                        auxlabel += "[{0}]\n".format(child.surface)
                else:
                    if not sub and child.type in EntityTypeDict:
                        sub = child
                    elif not obj and child.type in EntityTypeDict:
                        obj = child
                    else:
                        aux.append(child.id)
                        auxlabel += "[{0}]\n".format(child.surface)
            elif child.func in ObjPassiveSubDict:
                if parent.passive == 1:
                    if not sub and child.type in EntityTypeDict:
                        sub = child
                    elif not obj and child.type in EntityTypeDict:
                        obj = child
                    else:
                        aux.append(child.id)
                        auxlabel += "[{0}]\n".format(child.surface)
                else:
                    if not obj and child.type in EntityTypeDict:
                        obj = child
                    elif not sub and child.type in EntityTypeDict:
                        sub = child
                    else:
                        aux.append(child.id)
                        auxlabel += "[{0}]\n".format(child.surface)
            else:
                aux.append(child.id)
                auxlabel += "[{0}]\n".format(child.surface)

        if parent.passive == 0:
            # Add parent and subject.
            # if sub and obj:
            #     parent.main = "<{0}>[{2}]{1}".format(sub.main, parent.main, obj.main)
            # elif sub:
            #     parent.main = "<{0}>[NONE]{1}".format(sub.main, parent.main)
            # elif obj:
            #     parent.main = "<NONE>[{1}]{0}".format(parent.main, obj.main)
            if sub:
                parent.main = "<{0}>{1}".format(sub.main, parent.main)
                self._addNode(parent, sub=sub.main)
                if not self.G.has_node(sub.main):
                    self._addNode(sub)
                self._addEdge(sub.main, parent.main, label="主体\n", etype="sub")
            else:
                self._addNode(parent)
            # Add object.
            if obj:
                if not self.G.has_node(obj.main):
                    self._addNode(obj)
                self._addEdge(parent.main, obj.main, label="客体\n" + auxlabel, etype="obj")
        else:
            # Add obj as sub
            # if sub and obj:
            #     parent.main = "<{0}>[{2}]{1}".format(sub.main, parent.main, obj.main)
            # elif obj:
            #     parent.main = "<{0}>[NONE]{1}".format(obj.main, parent.main)
            # elif sub:
            #     parent.main = "<NONE>[{1}]{0}".format(parent.main, sub.main)
            if obj:
                parent.main = "<{0}>{1}".format(obj.main, parent.main)
                self._addNode(parent, sub=obj.main)
                if not self.G.has_node(obj.main):
                    self._addNode(obj)
                self._addEdge(obj.main, parent.main, label="主体\n", etype="sub")
            else:
                self._addNode(parent)
            # Add sub as obj
            if sub:
                if not self.G.has_node(sub.main):
                    self._addNode(sub)
                self._addEdge(parent.main, sub.main, label="客体\n", etype="obj")
            # # Add obj as aux.
            # if obj:
            #     aux.append(obj.id)
            #     auxlabel += "[{0}]\n".format(obj.surface)
        self._processAux(aux, parent.main, chunks)        

    def _processAux(self, aux, pname, chunks):
        """Process aux list if any."""
        if len(aux) > 0:
            for nid in aux:
                if not self.G.has_node(chunks[nid].main):
                    self._addNode(chunks[nid])
                if chunks[nid].main[-2:] in ["ため", "為め", "爲め"] or chunks[nid].main[-1] in ["爲", "為"]:
                    self._addEdge(chunks[nid].main, pname, label="因果関係候補", etype="cause")
                else:
                    self._addEdge(chunks[nid].main, pname, label=chunks[nid].func, etype="aux")