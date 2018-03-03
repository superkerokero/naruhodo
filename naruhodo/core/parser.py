import re
import itertools
from multiprocessing import Pool
import networkx as nx
from nxpd import draw
from naruhodo.utils.scraper import NScraper
from naruhodo.utils.misc import exportToJsonFile
from naruhodo.utils.misc import getNodeProperties, getEdgeProperties
from naruhodo.core.DependencyCoreJa import DependencyCoreJa
from naruhodo.core.KnowledgeCoreJa import KnowledgeCoreJa

class parser(object):
    """The general parser for naruhodo."""
    def __init__(self, lang="ja", gtype="k", mp=False, nproc=0):
        """Constructor."""
        self.G = nx.DiGraph()
        """
        Graph object of the parser.
        It is actually a networkx directed graph object(DiGraph), so you can apply all operations available to DiGraph object using networkx.
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
        self.core.add(inp)
        self.G = self._mergeGraph(self.G, self.core.G)
        self.core.G.clear()

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
            self.core.add(inp)
        self.G = self._mergeGraph(self.G, self.core.G)
        self.core.G.clear()

    def _addAllMP(self, inps):
        """Parallel implementation of addAll function."""
        inps = [self._preprocessText(inp) for inp in inps]
        if self.lang == "ja":
            if self.gtype == "d":
                results = self.pool.map(self._addMP_ja_d, inps)
            elif self.gtype == "k":
                results = self.pool.map(self._addMP_ja_k, inps)
            else:
                raise ValueError("Unknown graph type: {0}".format(self.gtype))
        else:
            raise ValueError("Unsupported language: {0}".format(self.lang))
        print(self._reduce(results))
        self.G = self._mergeGraph(self.G, self._reduce(results))

    def _reduce(self, results):
        """Reduce the results from multiprocessing to final result."""
        args = list()
        if len(results) == 1:
            return results[0]
        if len(results) == 2:
            return self._mergeGraph(*results)
        elif len(results) % 2 == 0:
            for i in range(int(len(results) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(self._mergeGraph, args)
            return self._reduce(ret)
        else:
            for i in range(int((len(results) - 1) / 2)):
                args.append([results[i * 2], results[i * 2 + 1]])
            ret = self.pool.starmap(self._mergeGraph, args)
            ret.append(results[-1])
            return self._reduce(ret)

    @staticmethod
    def _addMP_ja_d(inp):
        """Static version of add for DSG parsing in Japanese."""
        core = DependencyCoreJa()
        core.add(inp)
        return core.G

    @staticmethod
    def _addMP_ja_k(inp):
        """Static version of add for KSG parsing in Japanese."""
        core = KnowledgeCoreJa()
        core.add(inp)
        return core.G

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