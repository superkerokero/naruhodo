from hinabe.utils.dicts import ProDict
import re

class CaboChunk(object):
    """Class for chunks"""
    def __init__(self, chunk_id, parent):
        """Initialize a chunk."""
        self.id = chunk_id    # id
        self.parent = parent  # parent chunk
        self.nouns = list()   # nouns 名詞
        self.verbs = list()   # verbs 動詞
        self.adjs = list()    # adjectives 形容詞
        self.postps = list()  # postpositions 助詞
        self.auxvs = list()   # auxilary verbs 助動詞
        self.conjs = list()   # conjection 接続詞
        self.interjs = list() # interjections 感動詞
        self.signs = list()   # signs 記号
        self.advs = list()    # adverbs 副詞
        self.main = ""
        self.func = ""
        """
        Type of this chunk.
        -------------------
        -1: unknown type
         0: noun
         1: adjective
         2: verb
         3: conjective
         4: interjection
         5: adverb
        """
        self.type = -1
        """
        Named entity type of this chunk.
        --------------------------------
        -1: no named entity(or unknown)
         0: person
         1: location
         2: organization
        """
        self.NE = -1
        """
        Pronoun type of this chunk. 
        ---------------------------
        -1: no pronoun(or unknown)
         0: demonstrative-loc
         1: demonstrative-obj
         2: personal(1st)
         3: personal(2nd)
         4: personal(3rd)
         5: indefinite
         6: inclusive
        """
        self.pro = -1
    
    def add(self, inp):
        """Add components to chunk lists."""
        elem = {
            'surface': inp[7],
            'labels': inp[2:7],
        }
        if inp[1] == "名詞":
            self.nouns.append(elem)
        elif inp[1] == "動詞":
            self.verbs.append(elem)
        elif inp[1] == "形容詞":
            self.adjs.append(elem)
        elif inp[1] == "助詞":
            self.postps.append(elem)
        elif inp[1] == "助動詞":
            self.auxvs.append(elem)
        elif inp[1] == "接続詞":
            self.conjs.append(elem)
        elif inp[1] == "感動詞":
            self.interjs.append(elem)
        elif inp[1] == "記号":
            self.signs.append(elem)
        elif inp[1] == "副詞":
            self.advs.append(elem)
        else:
            pass
        
    def _getMain(self):
        """Get the main component of the chunk."""
        if len(self.nouns) > 0:
            self.main = "".join([x['surface'] for x in self.nouns])
            self.type = 0
            # Corrections for special patterns.
            if self.nouns[0]['labels'][0] == 'サ変接続':
                self.type = 2
            elif self.nouns[0]['labels'][0] == '形容動詞語幹':
                self.type = 1
            # NE recognition.
            elif self.nouns[0]['labels'][0] == '固有名詞':
                if self.nouns[0]['labels'][1] == '人名':
                    self.NE = 0
                elif self.nouns[0]['labels'][1] == '地域':
                    self.NE = 1
                elif self.nouns[0]['labels'][1] == '組織':
                    self.NE = 2
                else:
                    pass
            # Pronoun identification(for correference analysis.)
            elif self.nouns[0]['labels'][0] == '代名詞':
                if self.nouns[0]['surface'] in ProDict['demonstrative-loc']:
                    self.pro = 0
                elif self.nouns[0]['surface'] in ProDict['demonstrative-obj']:
                    self.pro = 1
                elif self.nouns[0]['surface'] in ProDict['personal1st']:
                    self.pro = 2
                elif self.nouns[0]['surface'] in ProDict['personal2nd']:
                    self.pro = 3
                elif self.nouns[0]['surface'] in ProDict['personal3rd']:
                    self.pro = 4
                elif self.nouns[0]['surface'] in ProDict['indefinite']:
                    self.pro = 5
                elif self.nouns[0]['surface'] in ProDict['inclusive']:
                    self.pro = 6
                else:
                    pass
            else:
                pass
        elif len(self.adjs):
            self.main = self.adjs[0]['surface']
            self.type = 1
        elif len(self.verbs) > 0:
            self.main = self.verbs[0]['surface']
            self.type = 2
        elif len(self.conjs):
            self.main = self.conjs[0]['surface']
            self.type = 3
        elif len(self.interjs):
            self.main = self.interjs[0]['surface']
            self.type = 4
        elif len(self.advs):
            self.main = self.advs[0]['surface']
            self.type = 5
        else:
            pass
        
    def _getFunc(self):
        """Get the func component of the chunk."""
        if len(self.auxvs) > 0:
            self.func = "・".join([x['surface'] for x in self.auxvs])
            for elem in self.postps:
                if elem['labels'][0] == "終助詞" or elem['labels'][0] == "副助詞／並立助詞／終助詞" :
                    self.func += "~" + elem['surface']
            neg = sum([
                [x['surface'] for x in self.auxvs].count('ん'), 
                [x['surface'] for x in self.auxvs].count('ない'),
                [x['surface'] for x in self.auxvs].count('ぬ')
            ])
            if neg == 1:
                self.main += "(否定)"
            elif neg > 1:
                if neg % 2 == 0:
                    self.main += "(二重否定・強賛同)"
                else:
                    self.main += "(多重否定)"
            else:
                pass
        elif len(self.postps) > 0:
            self.func = "・".join([x['surface'] for x in self.postps])
        else:
            pass
        
    def processChunk(self):
        """Process the chunk to get main and func component of it."""
        self._getMain()
        self._getFunc()
    
class CabochaClient(object):
    """Class for CaboCha backend."""
    def __init__(self):
        """Initialize a native database."""
        self.rsplit = re.compile(r'[,]+|\t')
        self.chunks = list()
                
    def add(self, inp):
        """Takes in the block output from CaboCha and add it to native database."""
        ck = None
        for elem in inp.splitlines():
            if elem[0] == '*':
                if ck is not None:
                    ck.processChunk()
                    self.chunks.append(ck)
                ck = CaboChunk(*self._processHead(elem))
            else:
                ck.add(self.rsplit.split(elem))
        ck.processChunk()
        self.chunks.append(ck)
                
    def _processHead(self, inp):
        """Takes in the head of the chunk and process ids / parents."""
        elem = inp.split()
        return int(elem[1]), int(elem[2][:-1])
