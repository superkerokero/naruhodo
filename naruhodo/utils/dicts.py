"""
This module contains various dicts used in naruhodo.
"""


ProDict = {
    'demonstrative-loc': ["ここ", "そこ", "あそこ", "こっち", "そっち", "あっち", "こちら", "そちら", "あちら"],
    'demonstrative-obj': ["これ", "それ", "あれ", "こいつ", "そいつ", "あいつ"],
    'personal1st': ["私", "わたし", "俺", "おれ", "オレ", "僕", "ぼく", "ボク", "我ら", "我々"],
    'personal2nd': ["君", "きみ", "キミ", "あなた", "貴方", "お前"],
    'personal3rd': ["やつ", "奴", "彼", "彼女"],
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


NodeShape2JsonDict = {
    "square": "circle",
    "Mdiamond": "circle",
    "doublecircle": "circle",
    "parallelogram": "ellipse",
    "pentagon": "diamond",
    "box": "hexagon",
    "circle": "square",
    "underline": "text"
}
"""
Dict to convert the node shape from notebook to vis.js json format.
"""

EdgeType2StyleDict = {
    "none": "solid",
    "sub": "solid",
    "autosub": "solid",
    "obj": "dashed",
    "aux": "dotted",
    "cause": "dotted",
    "coref": "solid",
    "synonym": "solid"
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
    "synonym": "#00ffb6"
}
"""
Dict to convert the edge type to edge color.
"""


MeaninglessDict = set([
    "前", "後", "こと", "事", "もの", "物", "ため", "爲", "為", "為め", "爲め", 
    "意", "中", "なる", "成る", "ある", "よる", "する", "ない", "から", "だから"
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
    "は",
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

ObjPassiveSubDict = set([
    "へ", "と", "ないと", "とは"
])
"""
Dict that contains functional words that can be objects for normal verbs and subjects for passive verbs. 
"""

SubPassiveObjDict = set([
    "も",
])
"""
Dict that contains functional words that can be objects for normal verbs and subjects for passive verbs. 
"""

MultiRoleDict = set([
    "が", "などが"
])
"""
Dict that contains functional words that has multiple roles.
"""