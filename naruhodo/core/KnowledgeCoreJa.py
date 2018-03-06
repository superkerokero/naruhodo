import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CabochaClient
from naruhodo.utils.dicts import MeaninglessDict, AuxDict, SubDict, ObjDict, ObjPassiveSubDict, MultiRoleDict, SubPassiveObjDict, NEList

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
        self.rootsub = None
        """
        The subject node of the root. Used to assign subject node to parent nodes other than the root.
        """
        self.root_has_no_sub = False
        """
        If True, it means that root has no subject and has to transfer its children's subject(if any) to root.
        """
        self.rootname = ""
        """
        Name of the root node.
        """

    def add(self, inp, pos):
        """Take in a string input and add it to the knowledge structure graph(KSG)."""
        # Reset rootsub everytime you add a new piece of text.
        self.rootsub = None
        self.root_has_no_sub = False
        self.rootname = ""
        self.pos = pos
        # Call backend for dependency parsing.
        cabo = CabochaClient()
        cabo.add(self.proc.query(inp), self.pos)
        pool = [cabo.root]
        self.vlist = dict()
        # start while loop from root node
        while pool:
            # Take next id from pool as parent
            pid = pool.pop(0)
            for cid in cabo.childrenList[pid]:
                pool.append(cid)
            self._addChildren(pid, cabo.chunks)
        if self.root_has_no_sub:
            omitted = "省略される主語[{0}@{1}]".format(self.pos, 0)
            self._addNode(omitted, 0, omitted, 7, 0)
            self._addEdge(omitted, self.rootname, label="(省略)", etype="sub")

    def _addChildren(self, pid, chunks):
        """Add children following rules."""
        parent = chunks[pid]
        if parent.type in [0, 6]:
            # When parent node is noun/connect.
            self._addNoun(pid, chunks)
        elif parent.type in [1, 2, 5]:
            # When parent node is adj/verb.
            self._addVerbAdj(pid, chunks, mode="verb")
        else:
            pass

    def _addToVList(self, pname, child):
        """Add the verb-related edge to vlist to be added later."""
        try:
            self.vlist[child.main].append([pname, child.func])
        except KeyError:
            self.vlist[child.main] = [[pname, child.func]]

    def _addSpecial(self, pname, child):
        """Add special child node with extra information."""
        # Take care of special child that contains extra information
        if child.main[-2:] in ["ため", "為め", "爲め"] or child.main[-1] in ["爲", "為"]:
            self._addNode(child.main, child.type, child.main, child.pro, child.NE)
            self._addEdge(child.main, pname, label="因果関係候補", etype="aux")
        elif child.type in [1, 2, 5]:
            self._addToVList(pname, child)
        
    def _addNoun(self, pid, chunks):
        """Adding node/edge when parent node is noun."""
        parent = chunks[pid]
        if len(parent.children) == 0:
            return
        self._addNode(parent.main, parent.type, parent.main, parent.pro, parent.NE)
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.type in [3, 4, 6]:
                continue
            elif child.type in [1, 2, 5]:
                self._addToVList(parent.main, child)
            else:
                self._addNode(child.main, child.type, child.main, child.pro, child.NE)
                self._addEdge(child.main, parent.main, label=child.func, etype="none")
    
    def _addVerbAdj(self, pid, chunks, mode="verb"):
        """Adding node/edge when parent node is verb."""
        parent = chunks[pid]
        sub = None
        obj = None
        aux = list()
        auxlabel = ""
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.type in [3, 4, 5, 6]: # and child.type2 == -1:
                continue
            # Deal with passive form verb.
            if parent.passive == 1:
                if child.func in SubDict:
                    sub = child
                elif child.func in ObjDict:
                    obj = child
                elif child.func in MultiRoleDict:
                    if not sub:
                        sub = child
                    else:
                        obj = child
                elif child.func in ObjPassiveSubDict:
                    if not sub:
                        sub = child
                    else:
                        aux.append(child)
                        auxlabel += "\n{0}".format(child.surface)
                elif child.func in SubPassiveObjDict:
                    if not obj:
                        obj = child
                    else:
                        aux.append(child)
                        auxlabel += "\n{0}".format(child.surface)
                # elif child.func == "":
                #     if not sub:
                #         sub = child
                #     elif not obj:
                #         obj = child
                #     else:
                #         aux.append(child)
                #         auxlabel += "\n{0}".format(child.surface)
                # elif child.func in AuxDict:
                #     aux.append(child)
                #     auxlabel += "\n{0}".format(child.surface)
                elif child.type not in [1, 2, 5]:
                    aux.append(child)
                    auxlabel += "\n{0}".format(child.surface)
                else:
                    pass
            elif child.func in SubDict:
                sub = child
            elif child.func in ObjDict:
                obj = child
            elif child.func in SubPassiveObjDict:
                if not sub:
                    sub = child
                else:
                    aux.append(child)
                    auxlabel += "\n{0}".format(child.surface)
            elif child.func in MultiRoleDict:
                if not sub:
                    sub = child
                else:
                    obj = child
            elif child.func in ObjPassiveSubDict:
                if not obj:
                    obj = child
                else:
                    aux.append(child)
                    auxlabel += "\n{0}".format(child.surface)
            # elif child.func == "":
            #     if not sub:
            #         sub = child
            #     elif not obj:
            #         obj = child
            #     else:
            #         aux.append(child)
            #         auxlabel += "\n{0}".format(child.surface)
            # elif child.func in AuxDict:
            #     aux.append(child)
            #     auxlabel += "\n{0}".format(child.surface)
            elif child.type not in [1, 2, 5]:
                aux.append(child)
                auxlabel += "\n{0}".format(child.surface)
            else:
                pass

        if len(parent.children) == 0 and parent.parent == -1:
            for i in range(len(parent.children)):
                child = chunks[parent.children[i]]
                self._addSpecial(parent.main, child)
            self._processAux(aux, parent.main)
            return
        # Entities deemed as nouns.
        if sub:
            # sub.type = 0
            if not self.rootsub:
                self.rootsub = sub
                self._addNode(sub.main, sub.type, sub.main, sub.pro, sub.NE)
            if self.root_has_no_sub and parent.type == 2 and parent.type2 != 0:
                self._addEdge(self.rootsub.main, self.rootname, label="主語候補", etype="autosub")
                self.root_has_no_sub = False
        # if obj:
        #     obj.type = 0

        # Modify parent name with entities.
        if mode == "verb":
            pname = "{0}\n[{1}=>{2}]".format(parent.main, sub.main if sub else "None", obj.main if obj else "None")
        else:
            pname = parent.main
        self._addNode(pname, parent.type, parent.main, parent.pro, parent.NE)
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            self._addSpecial(pname, child)
        if sub:
            self._addNode(sub.main, sub.type, sub.main, sub.pro, sub.NE)
            self._addEdge(sub.main, pname, label=sub.func, etype="sub")
        elif parent.parent == -1:
            self.root_has_no_sub = True
            self.rootname = pname
        elif self.rootsub and parent.type == 2 and parent.type2 != 0:
            self._addEdge(self.rootsub.main, pname, label="主語候補", etype="autosub")
        if obj:
            self._addNode(obj.main, obj.type, obj.main, obj.pro, obj.NE)
            self._addEdge(pname, obj.main, label=auxlabel, etype="obj")
        self._processAux(aux, pname)
        if parent.main in self.vlist and len(self.vlist[parent.main]) > 0:
            for item in self.vlist[parent.main]:
                self._addEdge(pname, *item, etype="obj")
        # Add func edge for root.
        if parent.parent == -1:
            self._addEdge(pname, pname, label=parent.func, etype="none")

    def _processAux(self, aux, pname):
        """Process aux words and vlist if any."""
        if len(aux) > 0:
            for item in aux:
                self._addNode(item.main, item.type, item.main, item.pro, item.NE)
                self._addEdge(item.main, pname, label=item.func, etype="aux")
            
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
            
    def _addNode(self, name, ntype, rep, pro, NE):
        """Add node to node list"""
        # Add to entityList and proList.
        if pro != -1:
            bpos = name.find("[")
            rep = name[:bpos]
            proid = int(name[bpos+1:-1].split("@")[1])
            self.proList.append(dict(
                id = proid,
                name = name,
                rep = rep,
                type = pro,
                pos = self.pos
            ))
        elif ntype == 0:
            if rep in self.entityList[NE] and self.pos not in self.entityList[NE][name]:
                self.entityList[NE][name].append(self.pos)
            else:
                self.entityList[NE][name] = list([self.pos])
        # Add to graph.
        if self.G.has_node(name):
            if ntype in [0, 1, 2, 3, 4, 5]:
                if name not in MeaninglessDict:
                    self.G.nodes[name]['count'] += 1
                else:
                    self.G.nodes[name]['count'] == 1
        else:
            self.G.add_node(name, count=1, type=ntype, rep=rep, pro=pro, NE=NE)
        