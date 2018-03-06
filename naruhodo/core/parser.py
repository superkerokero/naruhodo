import re
import itertools
from multiprocessing import Pool
import networkx as nx
from nxpd import draw
from naruhodo.utils.scraper import NScraper
from naruhodo.utils.dicts import NEList
from naruhodo.utils.misc import exportToJsonFile
from naruhodo.utils.misc import getNodeProperties, getEdgeProperties, inclusive, harmonicSim
from naruhodo.core.DependencyCoreJa import DependencyCoreJa
from naruhodo.core.KnowledgeCoreJa import KnowledgeCoreJa

class parser(object):
    """The general parser for naruhodo."""
    def __init__(self, lang="ja", gtype="k", mp=False, nproc=0, wv=""):
        """Constructor."""
        self.G = nx.DiGraph()
        """
        Graph object of the parser.
        It is actually a networkx directed graph object(DiGraph), so you can apply all operations available to DiGraph object using networkx.
        """
        self.entityList = [dict() for x in range(len(NEList))]
        """
        List of entities appeared during this analysis.
        """
        self.proList = list()
        """
        List of pronouns appeared during this analysis.
        """
        self.pos = 0
        """
        Position of sentences added to the parser.
        """
        self.re_sent = re.compile(r'([^　！？。]*[！？。])')
        """
        Precompiled regular expression for separating sentences.
        """
        self._re1 = re.compile(r'\（.*?\）')
        self._re2 = re.compile(r'\[.*?\]')
        self._re3 = re.compile(r'\(.*?\)')
        """
        Precompiled regular expressions for getting rid of parenthesis.
        """
        self.lang = lang
        """
        Chosen language of the parser.
        ==============================
        'ja': Japanese
        'en': English(WIP)
        """
        self.gtype = gtype
        """
        Chosen graph type of the parser.
        ================================
        'd': dependency structure graph(DSG)
        'k': knowledge structure graph(KSG)
        """
        self.mp = mp
        """
        Use multiprocessing or not for parsing.
        """
        if self.lang == "ja":
            if self.gtype == "d":
                self.core = DependencyCoreJa()
            elif self.gtype == "k":
                self.core = KnowledgeCoreJa()
            else:
                raise ValueError("Unknown graph type: {0}".format(self.gtype))
        else:
            raise ValueError("Unsupported language: {0}".format(self.lang))
        if mp:
            if nproc == 0:
                self.pool = Pool()
            else:
                self.pool = Pool(processes=nproc)
        # load word vectors
        self.wv = None
        if wv != "":
            try:
                from gensim.models.word2vec import Word2Vec
                self.wv = Word2Vec.load(wv).wv
                print("Successfully loaded word vectors from given file: {0}.".format(wv))
            except ImportError:
                print("Failed to import gensim, please install it before trying to use word vector related functionalities.")

    def _parseToSents(self, context):
        """Parse given context into list of individual sentences."""
        return [sent.strip().replace('*', "-") for sent in self.re_sent.split(context) if sent.strip() != ""]

    def _grabTextFromUrls(self, urls):
        """Parse given url(or a list of urls) and return the text content of the it."""
        # Handle the single url case.
        if isinstance(urls, str):
            urls = [urls]
        # Initialize scraper.
        scpr = NScraper()
        ret = list()
        # loop through urls to extract text.
        for url in urls:
            text = scpr.getUrlContent(url)
            for block in text:
                for line in block.splitlines():
                    ret = list(itertools.chain(ret, self._parseToSents(line)))
        return ret

    def reset(self):
        """Reset the content of generated graph to empty."""
        self.G.clear()
        self.pos = 0
        self.entityList = [dict() for x in range(len(NEList))]
        # self.posEntityList = [dict() for x in range(len(NEList))]
        self.proList = list()

    def _preprocessText(self, text):
        """Get rid of weird parts from the text that interferes analysis."""
        # text = self._re1.sub("", text)
        text = self._re2.sub("", text)
        text = self._re3.sub("", text)
        return text

    def exportJSON(self, filename):
        """Export current graph to a JSON file on disk."""
        exportToJsonFile(self.G, filename)

    def _decorate(self):
        """Generate temporal graph with drawing properties added for nxpd."""
        ret = nx.DiGraph()
        for key, val in self.G.nodes.items():
            ret.add_node(key, **getNodeProperties(val))
        for key, val in self.G.edges.items():
            ret.add_edge(*key, **getEdgeProperties(val))
        return ret

    def show(self):
        '''Plot directional graph in jupyter notebook using nxpd.'''
        return draw(self._decorate(), show='ipynb')
    
    def plotToFile(self, filename):
        '''Output directional graph to a png file using nxpd.'''
        return draw(self._decorate(), filename=filename)

    def addUrls(self, urls):
        """Add the information from given urls to KSG."""
        context = self._grabTextFromUrls(urls)
        self.addAll(context)

    def add(self, inp):
        """Add a sentence to graph."""
        inp = self._preprocessText(inp)
        self.core.add(inp, self.pos)
        self.pos += 1
        self.G = self._mergeGraph(self.G, self.core.G)
        self.core.G.clear()
        self.entityList = self._mergeEntityList(self.entityList, self.core.entityList)
        self.core.entityList = [dict() for x in range(len(NEList))]
        self.proList = self._mergeProList(self.proList, self.core.proList)
        self.core.proList = list()

    def addAll(self, inps):
        """Add a list of sentences at once."""
        if self.mp:
            self._addAllMP(inps)
        else:
            self._addAllSP(inps)

    def _addAllSP(self, inps):
        """Standard implementation of addAll function."""
        for inp in inps:
            inp = self._preprocessText(inp)
            self.core.add(inp, self.pos)
            self.pos += 1
        self.G = self._mergeGraph(self.G, self.core.G)
        self.core.G.clear()
        self.entityList = self._mergeEntityList(self.entityList, self.core.entityList)
        self.core.entityList = [dict() for x in range(len(NEList))]
        self.proList = self._mergeProList(self.proList, self.core.proList)
        self.core.proList = list()

    def _addAllMP(self, inps):
        """Parallel implementation of addAll function."""
        inps = [[self.pos + x, self._preprocessText(inps[x])] for x in range(len(inps))]
        if self.lang == "ja":
            if self.gtype == "d":
                results = self.pool.starmap(self._addMP_ja_d, inps)
            elif self.gtype == "k":
                results = self.pool.starmap(self._addMP_ja_k, inps)
            else:
                raise ValueError("Unknown graph type: {0}".format(self.gtype))
        else:
            raise ValueError("Unsupported language: {0}".format(self.lang))
        self.pos += len(inps)
        final = self._reduce(results)
        self.G = self._mergeGraph(self.G, final[0])
        self.entityList = self._mergeEntityList(self.entityList, final[1])
        self.proList = self._mergeProList(self.proList, final[2])

    def _reduce(self, results):
        """Reduce the results from multiprocessing to final result."""
        args = list()
        if len(results) == 1:
            return results[0]
        if len(results) == 2:
            return self._mergeAll(*results)
        elif len(results) % 2 == 0:
            for i in range(int(len(results) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(self._mergeAll, args)
            return self._reduce(ret)
        else:
            for i in range(int((len(results) - 1) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(self._mergeAll, args)
            ret.append(results[-1])
            return self._reduce(ret)

    def resolve(self):
        """Resolve coreferences in the given text."""
        # Get flatten entity list
        flatEntityList = list()
        for item in self.entityList:
            for key in item.keys():
                flatEntityList.append(key)
        # Find syntatic synonyms
        for i in range(len(flatEntityList)):
            for j in range(i + 1, len(flatEntityList)):
                A = self._re3.sub("", flatEntityList[i]).replace("\n", "")
                B = self._re3.sub("", flatEntityList[j]).replace("\n", "")
                inc = inclusive(A, B)
                if inc == 1:
                    self.G.nodes[flatEntityList[i]]['count'] += 1
                    self.G.add_edge(flatEntityList[i], flatEntityList[j], weight=1, label="同義語候補", type="synonym")
                elif inc == -1:
                    self.G.nodes[flatEntityList[j]]['count'] += 1
                    self.G.add_edge(flatEntityList[j], flatEntityList[i], weight=1, label="同義語候補", type="synonym")
        # Get position-based entity list
        self.posEntityList = [dict() for x in range(len(NEList))]
        for i in range(len(NEList)):
            for key, val in self.entityList[i].items():
                for pos in val:
                    if pos in self.posEntityList[i]:
                        self.posEntityList[i][pos].append(key)
                    else:
                        self.posEntityList[i][pos] = list([key])
        # Resolve geolocations/persons
        for pro in self.proList:
            if pro['type'] == 0:
                antecedent = self._rresolve(pro['pos'] - 1, 2)
            elif pro['type'] in [2, 4]:
                antecedent = self._rresolve(pro['pos'] - 1, 1)
            elif pro['type'] == 7:
                if not self.wv:
                    print("Word vector model is not set correctly. Skipping part of coreference resolution.")
                    continue
                else:
                    antecedent = self._wvResolve(pro['name'], flatEntityList)
            if antecedent != "":
                self.G.nodes[antecedent]['count'] += 1
                self.G.add_edge(antecedent, pro['name'], weight=1, label="共参照候補", type="coref")

    def _rresolve(self, pos, NE):
        """Recursively resolve to previous position."""
        if pos == -1:
            return ""
        else:
            if pos in self.posEntityList[NE]:
                return self.posEntityList[NE][pos][-1]
            else:
                return self._rresolve(pos - 1, NE)

    def _wvResolve(self, proname, flatEntityList):
        """Resolve using word vector similarities."""
        ret = ""
        snames = list()
        svecs = list()
        sim = 0.
        for key in self.G.successors(proname):
            name = self._re3.sub("", key).replace("\n", "")
            if name in self.wv:
                snames.append(name)
                svecs.append(self.wv[name])
            for key2 in self.G.successors(key):
                name = self._re3.sub("", key2).replace("\n", "")
                if name in self.wv:
                    snames.append(name)
                    svecs.append(self.wv[name])
        if len(svecs) > 0:
            for item in flatEntityList:
                rawitem = self._re3.sub("", item).replace("\n", "")
                if rawitem not in snames and rawitem in self.wv:
                    score = harmonicSim(svecs, self.wv[rawitem])
                    if sim < score:
                        sim = score
                        ret = item
            if sim > 0.4:
                return ret
            else:
                return ""        
        else:
            return ""



    @staticmethod
    def _addMP_ja_d(pos, inp):
        """Static version of add for DSG parsing in Japanese."""
        core = DependencyCoreJa()
        core.add(inp, pos)
        return core.G, core.entityList, core.proList

    @staticmethod
    def _addMP_ja_k(pos, inp):
        """Static version of add for KSG parsing in Japanese."""
        core = KnowledgeCoreJa()
        core.add(inp, pos)
        return core.G, core.entityList, core.proList

    @staticmethod
    def _mergeGraph(A, B):
        """Return the merged graph of A and B."""
        for key, val in B.nodes.items():
            if A.has_node(key):
                A.nodes[key]['count'] += val['count']
            else:
                A.add_node(key, **val)
        for key, val in B.edges.items():
            if A.has_edge(*key):
                A.edges[key[0], key[1]]['weight'] += val['weight']
            else:
                A.add_edge(*key, **val)
        return A

    @staticmethod
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

    @staticmethod
    def _mergeProList(A, B):
        """Return merged proList os A and B."""
        for item in B:
            A.append(item)
        return A

    @staticmethod
    def _mergeAll(A, B):
        """Return merged result of graph, entity list and pronoun list."""
        # merge graph
        for key, val in B[0].nodes.items():
            if A[0].has_node(key):
                A[0].nodes[key]['count'] += val['count']
            else:
                A[0].add_node(key, **val)
        for key, val in B[0].edges.items():
            if A[0].has_edge(*key):
                A[0].edges[key[0], key[1]]['weight'] += val['weight']
            else:
                A[0].add_edge(*key, **val)
        # merge entity list
        for i in range(len(B[1])):
            for key, val in B[1][i].items():
                if key in A[1][i]:
                    for item in val:
                        A[1][i][key].append(item)
                else:
                    A[1][i][key] = val
        # merge pronoun list
        for item in B[2]:
            A[2].append(item)
        return A
        