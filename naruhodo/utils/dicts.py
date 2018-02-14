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
    'inclusive': ["皆", "みんな", "みな"]
}
"""
Pronoun identification dictionary.
"""


TypeList = ['名詞', '形容詞', '動詞', '接続詞', '感動詞', '副詞', '連体詞', '接頭詞']
"""
Dict of word types.
"""


NEList = ['PERSON', 'LOCATION', 'ORGANIZATION']
"""
Dict of named entity types.
"""


NodeShapeDictN2Json = {
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


MeaninglessDict = set([
    "前", "後", "こと", "もの", "ため", "意", "中", "なる", "ある", "よる", "する", "ない"
])
"""
Dict that contains meaningless entities that has to be integrated with its child properties to remain meaningful in the graph.
"""

VerbLikeFuncDict = set([
    "する", "しいるて", "し", "した", "しいるて・が", "いるて"
])