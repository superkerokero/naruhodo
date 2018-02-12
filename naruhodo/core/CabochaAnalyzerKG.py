import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CabochaClient
from naruhodo.utils.dicts import UncountedDict
from naruhodo.core.base import AnalyzerBase
from naruhodo.utils.misc import getNodeProperties, getEdgeProperties

class CabochaAnalyzerKG(AnalyzerBase):
    """Use cabocha as backend to analyze the input text and store the information into a DMG(Directed multi-graph)."""
    def __init__(self):
        """Setup a subprocess for using CaboCha as backend."""
        super().__init__()
        self.proc = Subprocess('cabocha -f1')
        
    def addToKG(self, inp):
        """Take in a string input and add it to the knowledge gragh(KG) using CaboCha as backend."""
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
            self._addChildren(cabo.chunks[pid], [cabo.chunks[cid] for cid in cabo.childrenList[pid]])
        self._updateKG()
            
    def _addChildren(self, parent, children):
        """Add children following rules."""
        if parent.type == 0:
            # When parent node is noun.
            self._addNoun(parent, children)
        elif parent.type in [1, 5, 6]:
            # When parent node is adj.
            self._addVerb(parent, children)
        elif parent.type == 2:
            # When parent node is verb.
            self._addVerb(parent, children)
        else:
            pass
        
    def _addNoun(self, parent, children):
        """Adding node/edge when parent node is noun."""
        if len(children) == 0:
            return
        self._addNode(parent.main, parent.type, parent.main)
        for child in children:
            # if child.type in [3, 4, 6]:
            #     continue
            if child.type == 2:
                try:
                    self.vlist[child.main].append([parent.main, child.func])
                except KeyError:
                    self.vlist[child.main] = [[parent.main, child.func]]
            else:
                self._addNode(child.main, child.type, child.main)
                self._addEdge(child.main, parent.main, child.func)
            
    def _addAdj(self, parent, children):
        """Adding node/edge when parent node is adj/adv."""
        pass
    
    def _addVerb(self, parent, children):
        """Adding node/edge when parent node is verb."""
        sub = None
        obj = None
        aux = ""
        for child in children:
            if child.type in [3, 4, 6]:
                continue
            if child.func in ["は", "には", "にも", "の"]:
                sub = child
            elif child.func in ["を", "に", "へ", "と", "ないと", "と・は"]:
                obj = child
            elif child.func in ["が", ]:
                if not sub:
                    sub = child
                else:
                    obj = child
            elif child.func in ["で", "によって"]:
                aux = child.surface
            else:
                pass
        if not sub and not obj:
            return
        pname = "{0}\n[{1}=>{2}]".format(parent.main, sub.main[0] if sub else "None", obj.main[0] if obj else "None")
        self._addNode(pname, parent.type, parent.main)
        if sub:
            self._addNode(sub.main, sub.type, sub.main)
            self._addEdge(sub.main, pname)
        else:
            # self._addNode("*省略される主語", 0, "*省略される主語")
            # self._addEdge("*省略される主語", pname)
            pass
        if obj:
            self._addNode(obj.main, obj.type, obj.main)
            self._addEdge(pname, obj.main, aux)
        if parent.main in self.vlist and len(self.vlist[parent.main]) > 0:
            for item in self.vlist[parent.main]:
                self._addEdge(pname, *item)
            
    def _addEdge(self, parent, child, label=""):
        """Add edge to edge list"""
        try:
            if parent not in UncountedDict and child not in UncountedDict:
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
                if name not in UncountedDict: 
                    self.nodes[name]['count'] += 1
                else:
                    self.nodes[name]['count'] == 1
        except KeyError:
            self.nodes[name] = {
                'count': 1,
                'type': ctype,
                'rep': rep,
                'len': len(name)
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
        """Add the information from given urls to DAG."""
        context = self._grabTextFromUrls(urls)
        for sent in context:
            self.addToKG(sent)