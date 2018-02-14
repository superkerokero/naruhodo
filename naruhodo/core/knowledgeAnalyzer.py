import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CabochaClient
from naruhodo.utils.dicts import MeaninglessDict
from naruhodo.core.base import AnalyzerBase
from naruhodo.utils.misc import getNodeProperties, getEdgeProperties

class KnowledgeAnalyzer(AnalyzerBase):
    """Analyze the input text and store the information into a knowledge graph(KG)."""
    def __init__(self):
        """Setup a subprocess for backend."""
        super().__init__()
        self.proc = Subprocess('cabocha -f1')
        
    def addToKG(self, inp):
        """Take in a string input and add it to the knowledge gragh(KG)."""
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
        self._updateKG()
            
    def _addChildren(self, pid, chunks):
        """Add children following rules."""
        parent = chunks[pid]
        if parent.type == 0:
            # When parent node is noun.
            self._addNoun(pid, chunks)
        elif parent.type in [1, 5, 6]:
            # When parent node is adj.
            self._addVerb(pid, chunks)
        elif parent.type == 2:
            # When parent node is verb.
            self._addVerb(pid, chunks)
        else:
            pass

    def _addToVList(self, pname, child):
        """Add the verb-related edge to vlist to be added later."""
        try:
            self.vlist[child.main].append([pname, child.func])
        except KeyError:
            self.vlist[child.main] = [[pname, child.func]]
        
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
            elif child.type == 2:
                self._addToVList(parent.main, child)
            else:
                self._addNode(child.main, child.type, child.main)
                self._addEdge(child.main, parent.main, child.func)
            
    def _addAdj(self, pid, chunks):
        """Adding node/edge when parent node is adj/adv."""
        pass
    
    def _addVerb(self, pid, chunks):
        """Adding node/edge when parent node is verb."""
        parent = chunks[pid]
        sub = None
        obj = None
        aux = ""
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.type in [2, 3, 4, 6] and child.type2 == -1:
                continue
            if child.func in ["は", "には", "にも", "の"]:
                sub = child
            elif child.func in ["を", ]:
                obj = child
            elif child.func in ["が", ]:
                if not sub:
                    sub = child
                else:
                    obj = child
            elif child.func in ["に", "へ", "と", "ないと", "と・は"]:
                if not obj:
                    obj = child
                else:
                    aux += "\n{0}".format(child.surface)
            elif child.func in ["で", "によって", "による", "により"]:
                aux += "\n{0}".format(child.surface)
            else:
                pass
        if not sub and not obj:
            return
        # Entities deemed as nouns.
        if sub:
            sub.type = 0
        if obj:
            obj.type = 0

        # Modify parent name with entities.
        pname = "{0}\n[{1}=>{2}]".format(parent.main, sub.main if sub else "None", obj.main if obj else "None")
        self._addNode(pname, parent.type, parent.main)
        for i in range(len(parent.children)):
            child = chunks[parent.children[i]]
            if child.type in [2, ]:
                self._addToVList(pname, child)
        if sub:
            self._addNode(sub.main, sub.type, sub.main)
            self._addEdge(sub.main, pname)
        elif parent.parent == -1:
            self._addNode("*省略される主語", 0, "*省略される主語")
            self._addEdge("*省略される主語", pname)
        if obj:
            self._addNode(obj.main, obj.type, obj.main)
            self._addEdge(pname, obj.main, aux)
        if parent.main in self.vlist and len(self.vlist[parent.main]) > 0:
            for item in self.vlist[parent.main]:
                self._addEdge(pname, *item)
            
    def _addEdge(self, parent, child, label=""):
        """Add edge to edge list"""
        try:
            if parent not in MeaninglessDict and child not in MeaninglessDict:
                self.edges[(parent, child)]['weight'] +=1
            else:
                self.edges[(parent, child)]['weight'] == 1
        except KeyError:
            self.edges[(parent, child)] = {
                'weight': 1,
                'label': label + ' ' # Add an empty character to avoid issues in javascript libraries.
            }
            
    def _addNode(self, name, ctype, rep):
        """Add node to node list"""
        try:
            if ctype in [0, 1, 2, 3, 4, 5]:
                if name not in MeaninglessDict: 
                    self.nodes[name]['count'] += 1
                else:
                    self.nodes[name]['count'] == 1
        except KeyError:
            self.nodes[name] = {
                'count': 1,
                'type': ctype,
                'rep': rep,
                'len': len(rep)
            }
            
    def _updateKG(self):
        """Update DMG using node/edge list."""
        # Add nodes to DAG.
        for key, val in self.nodes.items():
            self.G.add_node(key, **getNodeProperties(val))
        # Add edges to DAG.
        for key, val in self.edges.items():
            self.G.add_edge(*key, **getEdgeProperties(val))
            
    def addUrlsToKG(self, urls):
        """Add the information from given urls to KG."""
        context = self._grabTextFromUrls(urls)
        for sent in context:
            self.addToKG(sent)