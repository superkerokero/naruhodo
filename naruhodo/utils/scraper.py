"""
This module contains basic scraping functions.
"""

from bs4 import BeautifulSoup as bs
import urllib.request

class NScraper(object):
    '''Class for retrieving web contents.'''
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
            }
    
    def getUrlContent(self, url):
        '''Get string from url.'''
        req = urllib.request.Request(url=url, headers=self.headers)
        try:
            soup = bs(urllib.request.urlopen(req), "lxml")
            return ["".join([content.text for content in soup.find_all(['p', ])])]
            #return [content.text for content in soup.find_all(['p', ])]
        except:
            return ['503: service unavailable, try again later.']
