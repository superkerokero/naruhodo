import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CaboChunk, CabochaClient
from naruhodo.utils.dicts import MeaninglessDict, SubDict, ObjDict, ObjPostDict, ObjPassiveSubDict, SubPassiveObjDict, NEList, EntityTypeDict, ParallelDict

class KnowledgeCoreJa(object):
    """Analyze the input text and store the information into a knowledge structure graph(KSG)."""
    def __init__(self):
        """Initialize an analyzer for KSG."""
        self.G = nx.DiGraph()
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
        if chunks[pid].type == 0:
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
                # Add B properties to A
                for key in self.G.successors(pair[1]):
                    if key != pair[0]:
                        self._addEdge(pair[0], key, label=self.G.edges[pair[1], key]['label'], etype=self.G.edges[pair[1], key]['type'])

    def _addEntity(self, pid, chunks):
        """Add parent nodes that are nouns."""
        parent = chunks[pid]
        sub = None
        # Find subject
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.func in SubDict:
                sub = child
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
                continue
            elif child.type == 0 and child.func in ParallelDict:
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

        # Add parent and subject.
        if sub:
            parent.main = "{0}\n[{1}]".format(parent.main, sub.main)
            self._addNode(parent, sub=sub.main)
            if not self.G.has_node(sub.main):
                self._addNode(sub)
            self._addEdge(sub.main, parent.main, label="主体", etype="sub")
        else:
            # parent.main = "{0}\n[{1}]".format(parent.main, "")
            self._addNode(parent)
        # Add object.
        if obj:
            if not self.G.has_node(obj.main):
                self._addNode(obj)
            self._addEdge(parent.main, obj.main, label="客体\n" + auxlabel, etype="obj")
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
            
    def _addEdge(self, parent, child, label="", etype="none"):
        """Add edge to edge list"""
        if self.G.has_edge(parent, child):
            if parent not in MeaninglessDict and child not in MeaninglessDict:
                self.G.edges[parent, child]['weight'] +=1
            else:
                self.G.edges[parent, child]['weight'] == 1
        else:
            if label == "":
                label = " " # Assign a space to empty label to avoid problem in certain javascript libraries.
            self.G.add_edge(parent, child, weight=1, label=label, type=etype)
            
    def _addNode(self, node, sub=''):
        """Add node to node list"""
        # Get rep.
        bpos = node.main.find("[")
        if bpos == -1:
            rep = node.main
        else:
            rep = node.main[:bpos]
        # Add to proList.
        if node.pro != -1:
            proid = int(node.main[bpos+1:-1].split("@")[1])
            self.proList.append(dict(
                id = proid,
                name = node.main,
                rep = rep,
                type = node.pro,
                pos = self.pos
            ))
        # Add to entityList.
        elif node.type == 0:
            if node.main in self.entityList[node.NE] and self.pos not in self.entityList[node.NE][node.main]:
                self.entityList[node.NE][node.main].append(self.pos)
            else:
                self.entityList[node.NE][node.main] = [self.pos]
        # Add to graph.
        if self.G.has_node(node.main):
            if self.pos not in self.G.nodes[node.main]['pos']:
                self.G.nodes[node.main]['pos'].append(self.pos)
                self.G.nodes[node.main]['surface'].append(node.surface)
                self.G.nodes[node.main]['count'] += 1
        else:
            self.G.add_node(node.main, 
                            count = 1, 
                            func = node.func, 
                            type = node.type, 
                            label = rep, 
                            pro = node.pro, 
                            NE = node.NE, 
                            pos = [self.pos], 
                            surface = [node.surface],
                            yomi = node.yomi,
                            sub = sub,
                            meaning = node.meaning)