import re
import itertools
import networkx as nx
from nxpd import draw
from naruhodo.utils.scraper import NScraper
from naruhodo.utils.misc import exportToJsonFile

class AnalyzerBase(object):
    """Prototype of the analyzer classes."""
    def __init__(self):
        """Constructor."""
        self.G = nx.DiGraph()
        """
        Graph object of this analyzer.
        It is actually a networkx directed graph object(DiGraph), so you can apply all operations available to DiGraph object using networkx.
        """

        self.nodes = dict()
        """
        Native list of nodes in the graph.
        """

        self.edges = dict()
        """
        Native list of edges in the graph.
        """

        self.re_sent = re.compile('([^　！？。]*[！？。])')
        """
        Precompiled regular expression for separating sentences.
        """

        # self.re_parentheses = re.compile('\（[^)]*\）')
        self._re1 = re.compile('\（[^)]*\）')
        self._re2 = re.compile('\[[^)]*\]')
        self._re3 = re.compile('\([^)]*\)')
        """
        Precompiled regular expressions for getting rid of parenthesis.
        """

    def _parseToSents(self, context):
        """Parse given context into list of individual sentences."""
        #return [self.re_parentheses.sub("", sent.strip()) for sent in self.re_sent.split(context) if self.re_parentheses.sub("", sent.strip()) != ""]
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
                try:
                    from polyglot.detect import Detector
                    lang = Detector(block).language.name
                    if lang != '日本語':
                        print("サポートされてない言語: {0}".format(lang))
                        continue
                except:
                    print("Polyglot unavailable. Language detection disabled.")
                for line in block.splitlines():
                    ret = list(itertools.chain(ret, self._parseToSents(line)))
        return ret

    def reset(self):
        """Reset the content of generated graph to empty."""
        self.G = nx.DiGraph()
        self.nodes = dict()
        self.edges = dict()

    def _preprocessText(self, text):
        """Get rid of weird parts from the text that interferes analysis."""
        text = self._re1.sub("", text)
        text = self._re2.sub("", text)
        text = self._re3.sub("", text)
        return text

    def exportJSON(self, filename):
        """Export current graph to a JSON file on disk."""
        exportToJsonFile(self.G, filename)

    def show(self):
        '''Plot directional graph in jupyter notebook using nxpd.'''
        # span = list(nx.weakly_connected_component_subgraphs(self.G))
        return draw(self.G, show='ipynb')
    
    def plotToFile(self, filename):
        '''Output directional graph to a png file using nxpd.'''
        return draw(self.G, filename=filename)