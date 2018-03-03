import networkx as nx
from naruhodo.utils.communication import Subprocess
from naruhodo.backends.cabocha import CabochaClient
from naruhodo.utils.dicts import MeaninglessDict

class DependencyCoreJa(object):
    """Analyze the input text and store the information into a dependency structure graph(DSG)."""
    def __init__(self):
        """Initialize an analyzer for DSG."""
        self.G = nx.DiGraph()
        """
        Graph object of this analyzer.
        It is actually a networkx directed graph object(DiGraph), so you can apply all operations available to DiGraph object using networkx.
        """
        self.proc = Subprocess('cabocha -f1')
        """
        Communicator to backend for DependencyAnalyzer.
        """
        
    def add(self, inp):
        """Take in a string input and add it to the DSG."""
        cabo = CabochaClient()
        cabo.add(self.proc.query(inp))
        for chunk in cabo.chunks:
            self._addNode(chunk.main, ntype=chunk.type, rep=chunk.main)
        for chunk in cabo.chunks:
            self._addEdge(chunk.main, cabo.chunks[chunk.parent].main, label=chunk.func)

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
            
    def _addNode(self, name, ntype, rep):
        """Add node to node list"""
        # print("Add node", name, ntype, rep)
        if self.G.has_node(name):
            if ntype in [0, 1, 2, 3, 4, 5]:
                if name not in MeaninglessDict:
                    self.G.nodes[name]['count'] += 1
                else:
                    self.G.nodes[name]['count'] == 1
        else:
            self.G.add_node(name, count=1, type=ntype, rep=rep)