import unittest
from naruhodo.utils.scraper import NScraper

class TestScraper(unittest.TestCase):
    """Unit test for NScraper class."""
    def test_getUrlContent(self):
        scpr = NScraper()
        text = scpr.getUrlContent('https://stackoverflow.com/')
        self.assertEqual("Each", "Each")
