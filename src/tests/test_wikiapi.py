# -*- coding: utf-8 -*-
import os
import shutil
from six.moves import urllib_parse
from wikiapi import WikiApi
import unittest


def assert_url_valid(url):
    if not bool(urllib_parse.urlparse(url).netloc):
        raise AssertionError('{} is not a valid URL'.format(url))


class TestWiki(unittest.TestCase):
    def setUp(self):
        self.wiki = WikiApi()
        self.results = self.wiki.find('Bill Clinton')
        self.article = self.wiki.get_article(self.results[0])

    def test_heading(self):
        assert self.article.heading == 'Bill Clinton'

    def test_image(self):
        assert_url_valid(url=self.article.image)

    def test_summary(self):
        assert len(self.article.summary) > 100

    def test_content(self):
        assert len(self.article.content) > 200

    def test_references(self):
        assert isinstance(self.article.references, list) is True

    def test_url(self):
        assert_url_valid(url=self.article.url)
        assert self.article.url == 'https://en.wikipedia.org/wiki/Bill_Clinton'

    def test_get_relevant_article(self):
        keywords = ['president', 'hilary']
        _article = self.wiki.get_relevant_article(self.results, keywords)

        assert 'Bill Clinton' in _article.heading
        assert len(_article.content) > 5000
        assert 'President Bill Clinton' in _article.content

    def test_get_relevant_article_no_result(self):
        keywords = ['hockey player']
        _article = self.wiki.get_relevant_article(self.results, keywords)
        assert _article is None

    def test__remove_ads_from_content(self):
        content = (
            'From Wikipedia, the free encyclopedia. \n\nLee Strasberg '
            '(November 17, 1901 2013 February 17, 1982) was an American '
            'actor, director and acting teacher.\n'
            'Today, Ellen Burstyn, Al Pacino, and Harvey Keitel lead this '
            'nonprofit studio dedicated to the development of actors, '
            'playwrights, and directors.\n\nDescription above from the '
            'Wikipedia article\xa0Lee Strasberg,\xa0licensed under CC-BY-SA, '
            'full list of contributors on Wikipedia.'
        )

        result_content = self.wiki._remove_ads_from_content(content)

        expected_content = (
            ' \n\nLee Strasberg '
            '(November 17, 1901 2013 February 17, 1982) was an American '
            'actor, director and acting teacher.\n'
            'Today, Ellen Burstyn, Al Pacino, and Harvey Keitel lead this '
            'nonprofit studio dedicated to the development of actors, '
            'playwrights, and directors.'
        )
        assert expected_content == result_content


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

        assert self._get_cache_size() == 0
        self.wiki.find('Bob Marley')
        assert self._get_cache_size() == 0


class TestUnicode(unittest.TestCase):
    def setUp(self):
        # using an Italian-Emilian locale that is full of unicode symbols
        self.wiki = WikiApi({'locale': 'eml'})
        self.res = self.wiki.find('Bulaggna')[0]
        self.article = None

    def test_search(self):
        # this is urlencoded.
        assert self.res == u'Bul%C3%A5ggna'

    def test_article(self):
        # unicode errors will likely blow in your face here
        assert self.wiki.get_article(self.res) is not None
