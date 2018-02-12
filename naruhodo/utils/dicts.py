"""
Pronoun identification dictionary.
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
Dict of word types.
"""
TypeList = ['名詞', '形容詞', '動詞', '接続詞', '感動詞', '副詞', '連体詞', '接頭詞']

"""
Dict of named entity types.
"""
NEList = ['PERSON', 'LOCATION', 'ORGANIZATION']

"""
Dict to convert the node shape from notebook to vis.js json format.
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
Dict of common words that are not cumulatively counted.
"""
UncountedDict = set([
    "なる", "ある", "よる", "する", "ない", "前", "後", "こと", "もの", "ため"
])

MeaninglessDict = set([
    "前", "後", "こと", "もの", "ため", "意", "中"
])