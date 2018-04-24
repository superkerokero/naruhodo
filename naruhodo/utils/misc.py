"""
Module for miscellaneous utility functions.
"""
import re
import json
from math import sqrt
import numpy as np
import networkx as nx
from nxpd import draw
from naruhodo.utils.dicts import NodeType2StyleDict, NodeType2ColorDict, NodeType2FontColorDict, EdgeType2StyleDict, EdgeType2ColorDict


_re_sent = re.compile(r'([^　！？。]*[！？。])')
"""
Precompiled regular expression for separating sentences.
"""
_re1 = re.compile(r'\（.*?\）')
_re2 = re.compile(r'\[.*?\]')
_re3 = re.compile(r'\(.*?\)')
_re4 = re.compile(r'\<.*?\>')
"""
Precompiled regular expressions for getting rid of parenthesis.
"""

def preprocessText(text):
    """Get rid of weird parts from the text that interferes analysis."""
    text = text.replace("\n", "").replace("|", "、").replace(" ", "").strip()
    text = _re1.sub("", text)
    text = _re2.sub("", text)
    text = _re3.sub("", text)
    text = _re4.sub("", text)
    return text

def parseToSents(context):
        """Parse given context into list of individual sentences."""
        return [sent.strip().replace('*', "-") for sent in _re_sent.split(context) if sent.strip() != ""]

def exportToJsonObj(G):
    """Export given networkx graph to JSON object(dict object in python)."""
    return nx.node_link_data(G)

def exportToJsonFile(G, filename):
    """Export given networkx graph to JSON file."""
    with open(filename, 'w') as outfile:
        json.dump(exportToJsonObj(G), outfile)
    
def getNodeProperties(info, depth=False):
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
    if depth:
        d = np.average(info['depth']) # Average depth of the node
        d = min(d, 5.) # Normalize d to a range of [0, 6]
        cs = [255, 80, 0] # Base reference color at start
        ct = [255, 255, 255] # Base reference color at end
        cn = [0, 0, 0] # Average depth scaled node color
        for i in range(3):
            cn[i] = cs[i] + int((ct[i] - cs[i]) / 5. * d)
        ret['fillcolor'] = rgb2Hex(cn)
        ret['fontcolor'] = '#000000'
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

def decorate(G, depth, rankdir):
    """Generate temporal graph with drawing properties added for nxpd."""
    ret = nx.DiGraph()
    ret.graph['rankdir'] = rankdir
    for key, val in G.nodes.items():
        ret.add_node(key, **getNodeProperties(val, depth))
    for key, val in G.edges.items():
        ret.add_edge(*key, **getEdgeProperties(val))
    return ret

def show(G, depth=False, rankdir='TB'):
    """Decorate and draw given graph using nxpd in notebook."""
    return draw(decorate(G, depth, rankdir), show='ipynb')

def plotToFile(G, filename, depth=False, rankdir='TB'):
    """Output given graph to a png file using nxpd."""
    return draw(decorate(G, depth, rankdir), filename=filename)

def _mergeGraph(A, B):
    """Return the merged graph of A and B."""
    for key, val in B.nodes.items():
        if A.has_node(key):
            A.nodes[key]['count'] += val['count']
            for i in range(len(val['pos'])):
                if val['pos'][i] not in A.nodes[key]['pos']:
                    A.nodes[key]['pos'].append(val['pos'][i])
                    A.nodes[key]['lpos'].append(val['lpos'][i])
                    A.nodes[key]['func'].append(val['func'][i])
                    A.nodes[key]['surface'].append(val['surface'][i])
                    A.nodes[key]['yomi'].append(val['yomi'][i])
                    if 'depth' in A.nodes[key]:
                        A.nodes[key]['depth'].append(val['depth'][i])
        else:
            A.add_node(key, **val)
    for key, val in B.edges.items():
        if A.has_edge(*key):
            A.edges[key[0], key[1]]['weight'] += val['weight']
        else:
            A.add_edge(*key, **val)
    return A

def _mergeEntityList(A, B):
    """Return merged entityList os A and B."""
    for i in range(len(B)):
        for key, val in B[i].items():
            if key in A[i]:
                for item in val:
                    A[i][key].append(item)
            else:
                A[i][key] = val
    return A

def _mergeProList(A, B):
    """Return merged proList os A and B."""
    for item in B:
        A.append(item)
    return A

def _mergeAll(A, B):
    """Return merged result of graph, entity list and pronoun list."""
    A[0] = _mergeGraph(A[0], B[0])
    A[1] = _mergeEntityList(A[1], B[1])
    A[2] = _mergeProList(A[2], B[2])
    return A

def hex2Rgb(c):
    """
    Convert hex color in #XXXXXX format to RGB list.
    """
    return [int(c.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)]

def rgb2Hex(c):
    """
    Convert color in RGB format to hex format.
    """
    return "#{0:02x}{1:02x}{2:02x}".format(clamp(c[0]), clamp(c[1]), clamp(c[2]))

def clamp(x): 
    """
    Clamp x to 0 <= x <= 255.
    """
    return max(0, min(x, 255))