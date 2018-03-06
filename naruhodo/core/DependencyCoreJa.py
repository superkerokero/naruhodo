import networkx as nx
from naruhodo.utils.dicts import NEList
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
        Communicator to backend for DependencyAnalyzer.
        """
        
    def add(self, inp, pos):
        """Take in a string input and add it to the DSG."""
        cabo = CabochaClient()
        self.pos = pos
        cabo.add(self.proc.query(inp), self.pos)
        for chunk in cabo.chunks:
            self._addNode(chunk.main, chunk.type, chunk.main, chunk.pro, chunk.NE)
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