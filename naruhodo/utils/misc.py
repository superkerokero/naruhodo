"""
Module for miscellaneous utility functions.
"""
import json
from math import sqrt
import numpy as np
import networkx as nx
from naruhodo.utils.dicts import NodeType2StyleDict, NodeType2ColorDict, NodeType2FontColorDict, EdgeType2StyleDict, EdgeType2ColorDict

def exportToJsonObj(G):
    """Export given networkx graph to JSON object(dict object in python)."""
    return nx.node_link_data(G)

def exportToJsonFile(G, filename):
    """Export given networkx graph to JSON file."""
    with open(filename, 'w') as outfile:
        json.dump(exportToJsonObj(G), outfile)
    
def getNodeProperties(info):
    """Convert node properties for node drawing using nxpd."""
    ret = dict()
    ret['shape'] = NodeType2StyleDict[info['type']]
    ret['fillcolor'] = NodeType2ColorDict[info['type']]
    ret['fontcolor'] = NodeType2FontColorDict[info['type']]
    ret['label'] = info['label']
    ret['style'] = 'filled'
    ret['fixedsize'] = True 
    ret['fontsize'] = (5.0 + 20.0 / len(info['label'])) * info['count']
    ret['width'] = info['count']*0.75
    ret['count'] = info['count']
    return ret
    
def getEdgeProperties(info):
    """Convert edge properties for node drawing using nxpd."""
    ret = dict()
    ret['label'] = info['label']
    ret['penwidth'] = info['weight'] * 2.0
    ret['weight'] = info['weight']
    ret['style'] = EdgeType2StyleDict[info['type']]
    ret['color'] = EdgeType2ColorDict[info['type']]
    return ret

def inclusive(A, B):
    """Find if one of string A and B includes the other."""
    if len(A) > len(B):
        if A.find(B) != -1:
            ret = 1
        else:
            ret = 0
    elif len(A) < len(B):
        if B.find(A) != -1:
            ret = -1
        else:
            ret = 0
    else:
        ret = 0
    return ret

def cosSimilarity(A, B):
    """Compute the cosine similarity between vectors A and B."""
    return np.dot(A, B) / sqrt(np.dot(A, A) * np.dot(B, B))

def harmonicSim(AG, B):
    """Return the harmonic distance between a group of vectors AG and vector B."""
    size = len(AG)
    ret = 0.
    for i in range(size):
        ret += 1. / cosSimilarity(AG[i], B)
    return float(size) / ret