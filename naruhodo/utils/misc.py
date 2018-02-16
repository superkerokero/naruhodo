"""
Module for miscellaneous utility functions.
"""
import json
import networkx as nx
from naruhodo.utils.dicts import NodeShape2JsonDict, EdgeType2StyleDict, EdgeType2ColorDict

def exportToJsonObj(G):
    """Export given networkx graph to JSON object(dict object in python)."""
    raw = nx.node_link_data(G)
    ret = dict()
    ret['nodes'] = [{
        'id': item['id'],
        'label': item['label'],
        'value': item['width'],
        'title': item['count'],
        'shape': NodeShape2JsonDict[item['shape']],
        'color': {
            'background': item['fillcolor'],
            'highlight': '#ff9647',
            'hover': '#b4f3ff'
        },
        'font': {
            'color': item['fontcolor']
        }
    } for item in raw['nodes']]
    ret['edges'] = [{
        'from': item['source'],
        'to': item['target'],
        'label': item['label'],
        'arrows': 'to',
        'value': item['penwidth'],
        'title': item['weight'],
        'style': item['style']
    } for item in raw['links']]
    return ret

def exportToJsonFile(G, filename):
    """Export given networkx graph to JSON file."""
    with open(filename, 'w') as outfile:
        json.dump(exportToJsonObj(G), outfile)
    
def getNodeProperties(info):
    """Convert node properties for node drawing using nxpd."""
    ret = dict()
    ret['fontcolor'] = '#000000'
    if info['type'] == 0:
        ret['shape'] = 'square'
        ret['fillcolor'] = '#ffffff'
    elif info['type'] == 1:
        ret['shape'] = 'Mdiamond'
        ret['fillcolor'] = '#e5ffaa'
    elif info['type'] == 2:
        ret['shape'] = 'doublecircle'
        ret['fillcolor'] = '#000000'
        ret['fontcolor'] = '#ffffff'
    elif info['type'] == 3:
        ret['shape'] = 'parallelogram'
        ret['fillcolor'] = '#dcc4ff'
    elif info['type'] == 4:
        ret['shape'] = 'pentagon'
        ret['fillcolor'] = '#90889b'
    elif info['type'] == 5:
        ret['shape'] = 'box'
        ret['fillcolor'] = '#a3a8b7'
    elif info['type'] == 6:
        ret['shape'] = 'circle'
        ret['fillcolor'] = '#d0d4e0'
    else:
        ret['shape'] = 'underline'
        ret['color'] = '#ffffff'
    ret['label'] = info['rep']
    ret['style'] = 'filled'
    ret['fixedsize'] = True 
    ret['fontsize'] = (5.0 + 20.0 / info['len']) * info['count']
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