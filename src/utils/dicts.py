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

TypeList = ['名詞', '形容詞', '動詞', '接続詞', '感動詞', '副詞']
NEList = ['PERSON', 'LOCATION', 'ORGANIZATION']
