"""
This module contains various dicts used in naruhodo.
"""


ProDict = {
    'demonstrative-loc': ["ここ", "そこ", "あそこ", "こっち", "そっち", "あっち", "こちら", "そちら", "あちら"],
    'demonstrative-obj': ["これ", "それ", "あれ", "そう", "こう", "こんな", "そんな", "あんな"],
    'personal1st': ["私", "わたし", "俺", "おれ", "オレ", "僕", "ぼく", "僕ら", "ぼくら", "ボク", "我ら", "我々"],
    'personal2nd': ["君", "きみ", "キミ", "あなた", "貴方", "お前"],
    'personal3rd': ["やつ", "奴", "彼", "彼女", "こいつ", "そいつ", "あいつ"],
    'indefinite': ["どこ", "どれ", "どっち", "どなた", "どちら"],
    'inclusive': ["皆", "みんな", "みな"],
    'omitted': ["省略される主語"]
}
"""
Pronoun identification dictionary.
"""


TypeList = ['名詞', '形容詞', '動詞', '接続詞', '感動詞', '副詞', '連体詞', '接頭詞']
"""
Dict of word types.
"""


NEList = ['NONE', 'PERSON', 'LOCATION', 'ORGANIZATION', 'NUMBER']
"""
Dict of named entity types.
"""

NodeType2StyleDict = {
    -1: 'underline',
    0: 'square',
    1: 'Mdiamond',
    2: 'doublecircle',
    3: 'parallelogram',
    4: 'pentagon',
    5: 'box',
    6: 'circle'
}
"""
Dict to convert the node type to node style for visualization in notebook.
"""

NodeType2ColorDict = {
    -1: '#ffffff',
    0: '#ffffff',
    1: '#e5ffaa',
    2: '#000000',
    3: '#dcc4ff',
    4: '#90889b',
    5: '#a3a8b7',
    6: '#d0d4e0'
}
"""
Dict to convert the node type to node color for visualization in notebook.
"""

NodeType2FontColorDict = {
    -1: '#000000',
    0: '#000000',
    1: '#000000',
    2: '#ffffff',
    3: '#000000',
    4: '#000000',
    5: '#000000',
    6: '#000000'
}
"""
Dict to convert the node type to node font color for visualization in notebook.
"""

EdgeType2StyleDict = {
    "none": "solid",
    "sub": "solid",
    "autosub": "solid",
    "obj": "dashed",
    "aux": "dotted",
    "cause": "dotted",
    "coref": "solid",
    "synonym": "solid",
    "para": "solid",
    "attr": "dotted",
    "stat": "solid"
}
"""
Dict to convert the edge type to edge style.
"""

EdgeType2ColorDict = {
    "none": "#000000",
    "sub": "#000000",
    "autosub": "#aaaaaa",
    "obj": "#000000",
    "aux": "#ff7777",
    "cause": "#91027e",
    "coref": "#3582ff",
    "synonym": "#00ffb6",
    "para": "#207272",
    "attr": "#7738ff",
    "stat": "#66aaee"
}
"""
Dict to convert the edge type to edge color.
"""


MeaninglessDict = set([
    "前", "後", "こと", "事", "もの", "物", "者", "ため", "爲", "為", "為め", "爲め", 
    "意", "上", "うえ", "中", "なか", "下", "した", "なる", "成る", "ある", "よる", "する", 
    "ない", "無い", "から", "だから", "場合", "とき", "時", "程度", 
    "問題", "もんだい", "内容", "ないよう", "範囲", "やつ", "くる", "来る"
])
"""
Dict that contains meaningless entities that has to be integrated with its child properties to remain meaningful in the graph.
"""

VerbLikeFuncDict = set([
    "する", "しいるて", "し", "した", "しいるて・が", "いるて"
])
"""
Dict that contains verb-like functional words.
"""

AuxDict = set([
    "", "には", "にも", "だと", "の", "に", "で", "によって", 
    "による", "により", "で・の", "で・あるから", "だから", "から", 
    "まで", "も", "として", "しよするうとは", "だけ", "なので", "ですから"
])
"""
Dict that contains functional words of auxilaries.
"""

SubDict = set([
    "は", "では", "などは"
])
"""
Dict that contains functional words of subjects.
"""

ObjDict = set([
    "を", 
])
"""
Dict that contains functional words of objects.
"""

ObjPostDict = set([
    "へ", "に",
])
"""
Dict that contains functional words that can be objects. 
"""

ObjPassiveSubDict = set([
    "と", "ないと", "とは"
])
"""
Dict that contains functional words that can be objects for normal verbs and subjects for passive verbs. 
"""

SubPassiveObjDict = set([
    "が", "などが", "も"
])
"""
Dict that contains functional words that can be objects for normal verbs and subjects for passive verbs. 
"""

"""
Dict that contains functional words that has multiple roles.
"""

EntityTypeDict = set([0, 2])
"""
Dict of node types that can be potential entities.
"""

ParallelDict = set([
    "と", "などと", "や", "やら", "も", "、", "・", "｜"
])
"""
Dict that contains functional words that can be objects. 
"""