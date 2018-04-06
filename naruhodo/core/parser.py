import re
import itertools
from multiprocessing import Pool
import networkx as nx
from nxpd import draw
from naruhodo.utils.scraper import NScraper
from naruhodo.utils.dicts import NEList
from naruhodo.utils.misc import exportToJsonObj, exportToJsonFile
from naruhodo.utils.misc import inclusive, harmonicSim, cosSimilarity, show, plotToFile
from naruhodo.utils.misc import _mergeGraph, _mergeEntityList, _mergeProList, _mergeAll
from naruhodo.core.DependencyCoreJa import DependencyCoreJa
from naruhodo.core.KnowledgeCoreJa import KnowledgeCoreJa

class parser(object):
    """The general parser for naruhodo."""
    def __init__(self, lang="ja", gtype="k", mp=False, nproc=0, wv="", coref=False):
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

        self.coref = coref
        """
        If set to True, automatically resolve synonyms and coreferences after adding contexts.
        """

        self.corefDict = set()
        """
        A set that contains all possible antecedents of pronoun coreferences.
        """

        self.synonymDict = set()
        """
        A set that contains all roots(the shortest) of synonyms.
        """

        self._setCore()
        if mp:
            if nproc == 0:
                self.pool = Pool()
            else:
                self.pool = Pool(processes=nproc)
        # load word vectors
        self.wv = None
        """
        The word vector dictionary loaded from external model files.
        """
        if wv != "":
            try:
                from gensim.models.word2vec import Word2Vec
                self.wv = Word2Vec.load(wv).wv
                print("Successfully loaded word vectors from given file: {0}.".format(wv))
            except ImportError:
                print("Failed to import gensim, please install it before trying to use word vector related functionalities.")

    def change(self, lang, gtype):
        """Change the language and type of the parser."""
        self.lang = lang
        self.gtype = gtype
        self._setCore()

    def _setCore(self):
        """Set the core of the parser to chosen languange ang gtype."""
        if self.lang == "ja":
            if self.gtype == "d":
                self.core = DependencyCoreJa()
            elif self.gtype == "k":
                self.core = KnowledgeCoreJa(autosub=self.coref)
            else:
                raise ValueError("Unknown graph type: {0}".format(self.gtype))
        else:
            raise ValueError("Unsupported language: {0}".format(self.lang))

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
        self.posEntityList = [dict() for x in range(len(NEList))]
        self.proList = list()
        self.corefDict = set()
        self.synonymDict = set()

    def _preprocessText(self, text):
        """Get rid of weird parts from the text that interferes analysis."""
        text = self._re1.sub("", text)
        text = self._re2.sub("", text)
        text = self._re3.sub("", text)
        text = text.replace("・", "、").replace("|", "、").replace(" ", "").strip()
        return text.replace("\n", "")

    def exportObj(self):
        """Export graph to a JSON-like object for external visualization."""
        return exportToJsonObj(self.G)

    def exportJSON(self, filename):
        """Export current graph to a JSON file on disk."""
        exportToJsonFile(self.G, filename)

    def _path2Graph(self, path):
        """
        Generate a subgraph from the given path.
        """
        G = nx.DiGraph()
        for i in range(len(path)):
            if self.G.has_node(path[i]):
                G.add_node(path[i], **self.G.nodes[path[i]])
                # Add given edges
                try:
                    G.add_node(path[i+1], **self.G.nodes[path[i]])
                    G.add_edge(path[i], path[i+1], **self.G.edges[path[i], path[i+1]])
                except:
                    pass
                # Add predecessors and successors(KSG only)
                if self.gtype != "k":
                    continue
                for pred in self.G.predecessors(path[i]):
                    if self.G.edges[pred, path[i]]['type'] in ['sub', 'aux', 'cause']:
                        G.add_node(pred, **self.G.nodes[pred])
                        G.add_edge(pred, path[i], **self.G.edges[pred, path[i]])
                for succ in self.G.successors(path[i]):
                    if self.G.edges[path[i], succ]['type'] in ['obj', 'stat', 'attr']:
                        G.add_node(succ, **self.G.nodes[succ])
                        G.add_edge(path[i], succ, **self.G.edges[path[i], succ])
            else:
                print("'{0}' is not in generated graph!".format(path[i]))
        return G

    @staticmethod
    def _graph2Text(G):
        """
        Convert given semantic graph back to texts.
        """
        # Get distribution of sent positions in the graph as a dict.
        pdict = dict()
        for node in G.nodes:
            for pos in G.nodes[node]['pos']:
                try:
                    pdict[pos] += 1
                except KeyError:
                    pdict[pos] = 1
        # Sort dpos and get rid of sent positions that appeared only once.
        plist = sorted([pos for pos in pdict.keys() if pdict[pos] > 1])
        tdict = dict()
        # Get texts based on sent positions.
        for node in G.nodes:
            for i in range(len(G.nodes[node]['pos'])):
                if G.nodes[node]['pos'][i] in plist:
                    try:
                        tdict[G.nodes[node]['pos'][i]].append((G.nodes[node]['lpos'][i], G.nodes[node]['surface'][i]))
                    except KeyError:
                        tdict[G.nodes[node]['pos'][i]] = [(G.nodes[node]['lpos'][i], G.nodes[node]['surface'][i])]
        # Generate text based on local positions.
        ret = list()
        for key, val in tdict.items():
            raw = sorted(val, key=lambda x:x[0])
            ret.append([key, "".join([item[1] for item in raw])])
        return sorted(ret, key=lambda x:x[0])

    def toText(self, path=None):
        """
        If path is given, generate texts from the given path.
        Otherwise, generate texts using the entire graph.
        """
        if path:
            return self._graph2Text(self._path2Graph(path))
        else:
            return self._graph2Text(self.G)

    def show(self, path=None, depth=False):
        """
        If given a path, plot the subgraph generated from path.
        Otherwise, plot the entire graph.
        """
        # Sanity check for depth
        if depth and self.gtype != "d":
            print("Only dependency structure graph can be plotted with depth!")
            return
        if path:
            return show(self._path2Graph(path), depth=depth)
        else:
            return show(self.G, depth=depth)

    def plotToFile(self, path=None, filename=None):
        """
        If given a path, plot the subgraph generated from path to (png) file with given filename.
        Otherwise, plot the entire graph to (png) file with given filename.
        """
        if path:
            return plotToFile(self._path2Graph(path), filename)
        else:
            return plotToFile(self.G, filename)

    def addUrls(self, urls):
        """Add the information from given urls to KSG."""
        context = self._grabTextFromUrls(urls)
        self.addAll(context)
        return [self._preprocessText(item) for item in context]

    def add(self, inp):
        """Add a sentence to graph."""
        inp = self._preprocessText(inp)
        if inp == "":
            return [inp]
        self.core.add(inp, self.pos)
        self.pos += 1
        self.G = _mergeGraph(self.G, self.core.G)
        self.core.G.clear()
        self.entityList = _mergeEntityList(self.entityList, self.core.entityList)
        self.core.entityList = [dict() for x in range(len(NEList))]
        self.proList = _mergeProList(self.proList, self.core.proList)
        self.core.proList = list()
        if self.coref:
            self.resolve()
        return [inp]

    def addAll(self, inps):
        """Add a list of sentences at once."""
        if self.mp:
            self._addAllMP(inps)
        else:
            self._addAllSP(inps)
        if self.coref:
            self.resolve()

    def _addAllSP(self, inps):
        """Standard implementation of addAll function."""
        for inp in inps:
            inp = self._preprocessText(inp)
            if inp == "":
                continue
            self.core.add(inp, self.pos)
            self.pos += 1
        self.G = _mergeGraph(self.G, self.core.G)
        self.core.G.clear()
        self.entityList = _mergeEntityList(self.entityList, self.core.entityList)
        self.core.entityList = [dict() for x in range(len(NEList))]
        self.proList = _mergeProList(self.proList, self.core.proList)
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
        self.G = _mergeGraph(self.G, final[0])
        self.entityList = _mergeEntityList(self.entityList, final[1])
        self.proList = _mergeProList(self.proList, final[2])

    def _reduce(self, results):
        """Reduce the results from multiprocessing to final result."""
        args = list()
        if len(results) == 1:
            return results[0]
        if len(results) == 2:
            return _mergeAll(*results)
        elif len(results) % 2 == 0:
            for i in range(int(len(results) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(_mergeAll, args)
            return self._reduce(ret)
        else:
            for i in range(int((len(results) - 1) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(_mergeAll, args)
            ret.append(results[-1])
            return self._reduce(ret)

    def resolve(self):
        """Resolve coreferences in the given text."""
        # initialize a graph of synonym
        GS = nx.Graph()
        # Get flatten entity list
        flatEntityList = list()
        for item in self.entityList:
            for key in item.keys():
                flatEntityList.append(key)
        # Find syntatic synonyms
        for i in range(len(flatEntityList)):
            for j in range(i + 1, len(flatEntityList)):
                A = self._preprocessText(flatEntityList[i])
                B = self._preprocessText(flatEntityList[j])
                inc = inclusive(A, B)
                if not self.wv:
                    sim = 1.
                    print("Word vector model is not set correctly. Skipping part of coreference resolution.")
                else:
                    if A in self.wv and B in self.wv:
                        sim = cosSimilarity(self.wv[A], self.wv[B])
                    else:
                        sim = 1.
                if inc == 1 and sim > 0.5:
                    # self.G.nodes[flatEntityList[i]]['count'] += 1
                    GS.add_edge(flatEntityList[i], flatEntityList[j])
                    self.G.add_edge(flatEntityList[i], flatEntityList[j], weight=1, label="同義語候補", type="synonym")
                elif inc == -1 and sim > 0.5:
                    # self.G.nodes[flatEntityList[j]]['count'] += 1
                    GS.add_edge(flatEntityList[i], flatEntityList[j])
                    self.G.add_edge(flatEntityList[j], flatEntityList[i], weight=1, label="同義語候補", type="synonym")
        # Process GS
        for subG in nx.connected_components(GS):
            lshort = 10000
            nshort = ""
            for node in subG:
                if lshort > len(node):
                    lshort = len(node)
                    nshort = node
            self.synonymDict.add(nshort)
            for node in subG:
                self.G.nodes[node]['synonym'] = nshort
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
        while self.proList:
            pro = self.proList.pop(0)
            antecedent = ""
            if pro['type'] == 0:
                antecedent = self._rresolve(pro['pos'] - 1, 2)
            elif pro['type'] in [2, 4]:
                antecedent = self._rresolve(pro['pos'] - 1, 1)
            elif pro['type'] == 7:
                if not self.wv:
                    print("Word vector model is not set correctly. Skipping part of coreference resolution.")
                else:
                    antecedent = self._wvResolve(pro['name'], flatEntityList)
            # Process antecedent
            if antecedent != "":
                self.G.nodes[antecedent]['count'] += 1
                self.G.add_edge(antecedent, pro['name'], weight=1, label="共参照候補", type="coref")
            else:
                # Add unknown coref
                antecedent = "未知の主体"
                if not self.G.has_node(antecedent):
                    self.G.add_node(antecedent, 
                            count = 1, 
                            func = "(未知)", 
                            type = 0, 
                            label = antecedent, 
                            pro = -1, 
                            NE = 0, 
                            pos = [self.pos - 1], 
                            surface = [antecedent],
                            sub = "",
                            meaning = "")
                else:
                    self.G.nodes[antecedent]['count'] += 1
                self.G.add_edge(antecedent, pro['name'], weight=1, label="共参照候補", type="coref")
            # Add antecedent to corefDict
            self.corefDict.add(antecedent)

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
            name = self._preprocessText(key)
            if name in self.wv:
                snames.append(name)
                svecs.append(self.wv[name])
            for key2 in self.G.successors(key):
                name = self._preprocessText(key2)
                if name in self.wv:
                    snames.append(name)
                    svecs.append(self.wv[name])
        if len(svecs) > 0:
            for item in flatEntityList:
                rawitem = self._preprocessText(item)
                if rawitem not in snames and rawitem in self.wv:
                    score = harmonicSim(svecs, self.wv[rawitem])
                    if sim < score:
                        sim = score
                        ret = item
            if sim > 0.5:
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