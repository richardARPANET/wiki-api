# -*- coding: utf-8 -*-
from wikiapi import WikiApi
import unittest

wiki = WikiApi({})
results = wiki.find('Bill Clinton')
article = wiki.get_article(results[0])  # taking first search result


class TestWiki(unittest.TestCase):
    def test_heading(self):
        self.assertIsNotNone(article.heading)

    def test_image(self):
        self.assertTrue(isinstance(article.image, str))

    def test_summary(self):
        self.assertGreater(len(article.summary), 100)

    def test_content(self):
        self.assertGreater(len(article.content), 200)

    def test_references(self):
        self.assertTrue(isinstance(article.references, list))

    def test_url(self):
        self.assertTrue(article.url, u"http://en.wikipedia.org/wiki/Bill_Clinton")

    def test_get_relevant_article(self):
        keywords = ['president', 'hilary']
        _article = wiki.get_relevant_article(results, keywords)
        self.assertTrue('Bill Clinton' in _article.heading)

    def test_get_relevant_article_no_result(self):
        keywords = ['hockey player']
        _article = wiki.get_relevant_article(results, keywords)
        self.assertIsNone(_article)


class TestUnicode(unittest.TestCase):
    def setUp(self):
        # using an Italian-Emilian locale that is full of unicode symbols
        self.wiki = WikiApi({'locale': 'eml'})
        self.res = self.wiki.find('Bulaggna')[0]
        self.article = None

    def test_search(self):
        # this is urlencoded.
        self.assertEqual(self.res, u'Bul%C3%A5ggna')

    def test_article(self):
        #unicode errors will likely blow in your face here
        self.assertIsNotNone(self.wiki.get_article(self.res))


if __name__ == '__main__':
    unittest.main()
