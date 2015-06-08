# -*- coding: utf-8 -*-
import os
import shutil

import pytest
from six.moves import urllib_parse
from wikiapi import WikiApi


def assert_url_valid(url):
    if not bool(urllib_parse.urlparse(url).netloc):
        raise AssertionError('{} is not a valid URL'.format(url))


class TestWiki(object):

    @pytest.fixture(scope='function')
    def set_up(self):
        wiki = WikiApi()
        results = wiki.find('Bill Clinton')
        article = wiki.get_article(results[0])
        return {
            'wiki': wiki,
            'results': results,
            'article': article,
        }

    def test_heading(self, set_up):
        assert set_up['article'].heading == 'Bill Clinton'

    def test_image(self, set_up):
        assert_url_valid(url=set_up['article'].image)

    def test_summary(self, set_up):
        results = set_up['wiki'].find('Tom Hanks')
        article = set_up['wiki'].get_article(results[0])

        expected_summary_start = (
            'Thomas Jeffrey "Tom" Hanks (born July 9, 1956) is an '
            'American actor and filmmaker.'
        )
        expected_summary_end = (
            'In 2004, he received the Stanley Kubrick Britannia Award for '
            'Excellence in Film from the British Academy of Film and '
            'Television Arts (BAFTA).'
        )
        assert article.summary.startswith(expected_summary_start) is True
        assert article.summary.endswith(expected_summary_end) is True

    def test_content(self, set_up):
        assert len(set_up['article'].content) > 200

    def test_references(self, set_up):
        assert isinstance(set_up['article'].references, list) is True

    def test_url(self, set_up):
        assert_url_valid(url=set_up['article'].url)
        assert (
            set_up['article'].url ==
            'https://en.wikipedia.org/wiki/Bill_Clinton'
        )

    def test_get_relevant_article(self, set_up):
        keywords = ['president', 'hilary']
        _article = set_up['wiki'].get_relevant_article(
            set_up['results'], keywords)

        assert 'Bill Clinton' in _article.heading
        assert len(_article.content) > 5000
        assert 'President Bill Clinton' in _article.content

    def test_get_relevant_article_no_result(self, set_up):
        keywords = ['hockey player']
        _article = set_up['wiki'].get_relevant_article(
            set_up['results'], keywords)
        assert _article is None

    def test__remove_ads_from_content(self, set_up):
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

        result_content = set_up['wiki']._remove_ads_from_content(content)

        expected_content = (
            ' \n\nLee Strasberg '
            '(November 17, 1901 2013 February 17, 1982) was an American '
            'actor, director and acting teacher.\n'
            'Today, Ellen Burstyn, Al Pacino, and Harvey Keitel lead this '
            'nonprofit studio dedicated to the development of actors, '
            'playwrights, and directors.'
        )
        assert expected_content == result_content


class TestCache(object):

    def _get_cache_size(self, wiki_instance):
        """ Returns a count of the items in the cache """
        cache = os.path.exists(wiki_instance.cache_dir)
        if not cache:
            return 0
        _, _, cache_files = next(os.walk(wiki_instance.cache_dir))
        return len(cache_files)

    def test_cache_populated(self):
        """ Tests the cache is populated correctly """
        wiki = WikiApi({'cache': True, 'cache_dir': '/tmp/wikiapi-test'})

        assert self._get_cache_size(wiki) == 0
        # Make multiple calls to ensure no duplicate cache items created
        wiki.find('Bob Marley')
        wiki.find('Bob Marley')

        assert self._get_cache_size(wiki) == 1
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)

    def test_cache_not_populated_when_disabled(self):
        """ Tests the cache is not populated when disabled (default) """
        wiki = WikiApi({'cache': False})

        assert self._get_cache_size(wiki) == 0
        wiki.find('Bob Marley')
        assert self._get_cache_size(wiki) == 0
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)


class TestUnicode(object):

    @pytest.fixture(scope='function')
    def set_up(self):
        # using an Italian-Emilian locale that is full of unicode symbols
        wiki = WikiApi({'locale': 'eml'})
        result = wiki.find('Bulaggna')[0]
        return {
            'wiki': wiki,
            'result': result,
        }

    def test_search(self, set_up):
        # this is urlencoded.
        assert set_up['result'] == u'Bul%C3%A5ggna'

    def test_article(self, set_up):
        # unicode errors will likely blow in your face here
        assert set_up['wiki'].get_article(set_up['result']) is not None
