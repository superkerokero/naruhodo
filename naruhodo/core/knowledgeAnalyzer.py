import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CabochaClient
from naruhodo.utils.dicts import MeaninglessDict, AuxDict, SubDict, ObjDict, ObjPassiveSubDict, MultiRoleDict, SubPassiveObjDict
from naruhodo.core.base import AnalyzerBase
from naruhodo.utils.misc import getNodeProperties, getEdgeProperties

class KnowledgeAnalyzer(AnalyzerBase):
    """Analyze the input text and store the information into a knowledge structure graph(KSG)."""
    def __init__(self):
        """Setup a subprocess for backend."""
        super().__init__()
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

    def add(self, inp):
        """Take in a string input and add it to the knowledge structure graph(KSG)."""
        # Reset rootsub everytime you add a new piece of text.
        inp = self._preprocessText(inp)
        self.rootsub = None
        self.root_has_no_sub = False
        self.rootname = ""
        # Call backend for dependency parsing.
        cabo = CabochaClient()
        cabo.add(self.proc.query(inp))
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
            self._addNode("*省略される主語", -1, "*省略される主語")
            self._addEdge("*省略される主語", self.rootname, label="（省略）は", etype="sub")
        self._update()
            
    def _addChildren(self, pid, chunks):
        """Add children following rules."""
        parent = chunks[pid]
        if parent.type in [0, 5, 6]:
            # When parent node is noun/connect.
            self._addNoun(pid, chunks)
        elif parent.type in [1, 2]:
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
        if child.main[-2:] in ["ため", "爲", "為", "為め", "爲め"]:
            self._addNode(child.main, child.type, child.main)
            self._addEdge(child.main, pname, label="因果関係候補", etype="aux")
        elif child.type in [1, 2]:
            self._addToVList(pname, child)
        
    def _addNoun(self, pid, chunks):
        """Adding node/edge when parent node is noun."""
        parent = chunks[pid]
        if len(parent.children) == 0:
            return
        self._addNode(parent.main, parent.type, parent.main)
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.type in [3, 4, 6]:
                continue
            elif child.type in [1, 2]:
                self._addToVList(parent.main, child)
            else:
                self._addNode(child.main, child.type, child.main)
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
            if child.type in [3, 4, 6]: # and child.type2 == -1:
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
                # elif child.func in AuxDict:
                #     aux.append(child)
                #     auxlabel += "\n{0}".format(child.surface)
                elif child.type not in [1, 2]:
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
            # elif child.func in AuxDict:
            #     aux.append(child)
            #     auxlabel += "\n{0}".format(child.surface)
            elif child.type not in [1, 2]:
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
            sub.type = 0
            if not self.rootsub:
                self.rootsub = sub
            if self.root_has_no_sub and parent.type == 2 and parent.type2 != 0:
                self._addEdge(self.rootsub.main, self.rootname, label="主語候補", etype="autosub")
                self.root_has_no_sub = False
        if obj:
            obj.type = 0

        # Modify parent name with entities.
        if mode == "verb":
            pname = "{0}\n[{1}=>{2}]".format(parent.main, sub.main if sub else "None", obj.main if obj else "None")
        else:
            pname = parent.main
        self._addNode(pname, parent.type, parent.main)
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            self._addSpecial(pname, child)
        if sub:
            self._addNode(sub.main, sub.type, sub.main)
            self._addEdge(sub.main, pname, label=sub.func, etype="sub")
        elif parent.parent == -1:
            self.root_has_no_sub = True
            self.rootname = pname
        elif self.rootsub and parent.type == 2 and parent.type2 != 0:
            self._addEdge(self.rootsub.main, pname, label="主語候補", etype="autosub")
        if obj:
            self._addNode(obj.main, obj.type, obj.main)
            self._addEdge(pname, obj.main, label=auxlabel, etype="obj")
        self._processAux(aux, pname)
        if parent.main in self.vlist and len(self.vlist[parent.main]) > 0:
            for item in self.vlist[parent.main]:
                self._addEdge(pname, *item)
        # Add func edge for root.
        if parent.parent == -1:
            self._addEdge(pname, pname, label=parent.func, etype="none")

    def _processAux(self, aux, pname):
        """Process aux words and vlist if any."""
        if len(aux) > 0:
            for item in aux:
                self._addNode(item.main, item.type, item.main)
                self._addEdge(item.main, pname, label=item.func, etype="aux")
            
    def _addEdge(self, parent, child, label="", etype="none"):
        """Add edge to edge list"""
        try:
            if parent not in MeaninglessDict and child not in MeaninglessDict:
                self.edges[(parent, child)]['weight'] +=1
            else:
                self.edges[(parent, child)]['weight'] == 1
        except KeyError:
            self.edges[(parent, child)] = {
                'weight': 1,
                'label': label + ' ', # Add an empty character to avoid issues in javascript libraries.
                'type': etype
            }
            
    def _addNode(self, name, ntype, rep):
        """Add node to node list"""
        # print("Add node", name, ntype, rep)
        try:
            if ntype in [0, 1, 2, 3, 4, 5]:
                if name not in MeaninglessDict: 
                    self.nodes[name]['count'] += 1
                else:
                    self.nodes[name]['count'] == 1
        except KeyError:
            self.nodes[name] = {
                'count': 1,
                'type': ntype,
                'rep': rep,
                'len': len(rep)
            }
            
    def _update(self):
        """Update KSG using node/edge list."""
        # Add nodes to DAG.
        for key, val in self.nodes.items():
            self.G.add_node(key, **getNodeProperties(val))
        # Add edges to DAG.
        for key, val in self.edges.items():
            self.G.add_edge(*key, **getEdgeProperties(val))
            
    def addUrls(self, urls):
        """Add the information from given urls to KSG."""
        context = self._grabTextFromUrls(urls)
        for sent in context:
            self.add(sent)