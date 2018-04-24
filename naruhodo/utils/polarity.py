"""
This module contains polarity related functionalities.
"""
import pickle
import sys

class polarity(object):
    """
    Class for word and phrase polarity.
    """
    def __init__(self, lang='ja', pdict=''):
        """
        Constructor. If no pdict given, will initialize with an empty pdict.
        """
        self.lang = lang
        if pdict:
            pass
        else:
            self.pdict = dict()

    def load(self, fname):
        """
        Load saved polarity dict from file.
        """
        try:
            with open(fname, 'r') as f: 
                self.pdict = pickle.load(f)
        except:
            sys.exit('Failed loading pdict file: {0}. Please check the file path.'.format(fname))

    def save(self, fname):
        """
        Save polarity dict to file.
        """
        with open(fname, 'r') as f:
            pickle.dump(self.pdict, f)
