# -*- coding: utf-8 -*-
import os
import shutil
from wikiapi import WikiApi
import unittest


class TestWiki(unittest.TestCase):
    def setUp(self):
        self.wiki = WikiApi()
        self.results = self.wiki.find('Bill Clinton')
        self.article = self.wiki.get_article(self.results[0])

    def test_heading(self):
        self.assertIsNotNone(self.article.heading)

    def test_image(self):
        self.assertTrue(isinstance(self.article.image, str))

    def test_summary(self):
        self.assertGreater(len(self.article.summary), 100)

    def test_content(self):
        self.assertGreater(len(self.article.content), 200)

    def test_references(self):
        self.assertTrue(isinstance(self.article.references, list))

    def test_url(self):
        self.assertTrue(self.article.url,
                        "http://en.wikipedia.org/wiki/Bill_Clinton")

    def test_get_relevant_article(self):
        keywords = ['president', 'hilary']
        _article = self.wiki.get_relevant_article(self.results, keywords)
        self.assertTrue('Bill Clinton' in _article.heading)

    def test_get_relevant_article_no_result(self):
        keywords = ['hockey player']
        _article = self.wiki.get_relevant_article(self.results, keywords)
        self.assertIsNone(_article)


class TestCache(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree(self.wiki.cache_dir, ignore_errors=True)

    def _get_cache_size(self):
        """ Returns a count of the items in the cache """
        cache = os.path.exists(self.wiki.cache_dir)
        if not cache:
            return 0
        _, _, cache_files = next(os.walk(self.wiki.cache_dir))
        return len(cache_files)

    def test_cache_populated(self):
        """ Tests the cache is populated correctly """
        self.wiki = WikiApi({'cache': True, 'cache_dir': '/tmp/wikiapi-test'})

        self.assertEqual(self._get_cache_size(), 0)
        # Make multiple calls to ensure no duplicate cache items created
        self.wiki.find('Bob Marley')
        self.wiki.find('Bob Marley')

        self.assertEqual(self._get_cache_size(), 1)

    def test_cache_not_populated_when_disabled(self):
        """ Tests the cache is not populated when disabled (default) """
        self.wiki = WikiApi({'cache': False})

        self.assertEqual(self._get_cache_size(), 0)
        self.wiki.find('Bob Marley')
        self.assertEqual(self._get_cache_size(), 0)


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
