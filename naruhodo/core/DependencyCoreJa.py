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
            self._addNode(chunk)
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