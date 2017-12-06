import unittest
from utils.scraper import NScraper

class TestScraper(unittest.TestCase):
    def test_getUrlContent(self):
        scpr = NScraper()
        text = scpr.getUrlContent('https://github.com/superkerokero/hinabe')
        self.assertEqual(text[0].split()[0], "GitHub")
