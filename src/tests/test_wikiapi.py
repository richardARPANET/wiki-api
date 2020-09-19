# -*- coding: utf-8 -*-
import os
import shutil
from datetime import date

import pytest
import six
from six.moves import urllib_parse
from wikiapi import WikiApi


def assert_url_valid(url):
    if not bool(urllib_parse.urlparse(url).netloc):
        raise AssertionError(f'{url} is not a valid URL')


class TestWiki:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.wiki = WikiApi()
        self.results = self.wiki.find('Bill Clinton')
        self.article = self.wiki.get_article(self.results[0])

    def test_heading(self):
        assert self.article.heading == 'Bill Clinton'

    def test_image(self):
        assert_url_valid(url=self.article.image)

    def test_summary(self):
        results = self.wiki.find('Tom Hanks')
        article = self.wiki.get_article(results[0])

        assert 'Thomas' in article.summary
        assert 'Jeffrey' in article.summary
        assert 'Hanks' in article.summary

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

    def test_get_tables2(self, mocker):
        url = 'https://en.wikipedia.org/wiki/World_population'
        wiki = self.wiki

        tables = wiki.get_tables(url=url)
        assert tables

    def test_get_tables(self, mocker):
        url = (
            'https://en.wikipedia.org/wiki/'
            'COVID-19_pandemic_by_country_and_territory'
        )
        wiki = self.wiki

        tables = wiki.get_tables(url=url)

        assert tables
        assert isinstance(tables, dict)
        assert tuple(tables.keys()) == (
            f'COVID-19 pandemic by location {date.today().day} September 2020',
            'First COVID-19 cases by country or territory',
            'States with no confirmed COVID-19 cases',
            'Partially recognized states with no confirmed cases',
            'Dependencies with no confirmed cases',
        )
        assert tables['Dependencies with no confirmed cases'].T.to_dict() == {
            0: {
                'Rank': 1,
                'Territory': 'American Samoa',
                'Population': 56700,
                'Status': 'Unincorporated territory',
                'Country': 'United States',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            1: {
                'Rank': 2,
                'Territory': 'Cook Islands',
                'Population': 15200,
                'Status': 'Associated state',
                'Country': 'New Zealand',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            2: {
                'Rank': 3,
                'Territory': 'Wallis and Futuna',
                'Population': 11700,
                'Status': 'Overseas collectivity',
                'Country': 'France',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            3: {
                'Rank': 4,
                'Territory': 'Saint Helena, Ascension and Tristan da Cunha',
                'Population': 5633,
                'Status': 'Overseas territory',
                'Country': 'United Kingdom',
                'Continent': 'Africa',
                'Ref.': mocker.ANY,
            },
            4: {
                'Rank': 5,
                'Territory': 'Svalbard',
                'Population': 2667,
                'Status': 'Unincorporated area',
                'Country': 'Norway',
                'Continent': 'Europe',
                'Ref.': mocker.ANY,
            },
            5: {
                'Rank': 6,
                'Territory': 'Christmas Island',
                'Population': 1955,
                'Status': 'External territory',
                'Country': 'Australia',
                'Continent': 'Asia',
                'Ref.': mocker.ANY,
            },
            6: {
                'Rank': 7,
                'Territory': 'Norfolk Island',
                'Population': 1735,
                'Status': 'External territory',
                'Country': 'Australia',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            7: {
                'Rank': 8,
                'Territory': 'Niue',
                'Population': 1520,
                'Status': 'Associated state',
                'Country': 'New Zealand',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            8: {
                'Rank': 9,
                'Territory': 'Tokelau',
                'Population': 1400,
                'Status': 'Dependent territory',
                'Country': 'New Zealand',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            9: {
                'Rank': 10,
                'Territory': 'Cocos (Keeling) Islands',
                'Population': 555,
                'Status': 'External territory',
                'Country': 'Australia',
                'Continent': 'Asia',
                'Ref.': mocker.ANY,
            },
            10: {
                'Rank': 11,
                'Territory': 'Pitcairn Islands',
                'Population': 50,
                'Status': 'Overseas territory',
                'Country': 'United Kingdom',
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
        }
        assert tables[
            'States with no confirmed COVID-19 cases'
        ].T.to_dict() == {
            0: {
                'Rank': 1,
                'Country': 'North Korea[a]',
                'Population': 25778816,
                'Continent': 'Asia',
                'Ref.': mocker.ANY,
            },
            1: {
                'Rank': 2,
                'Country': 'Turkmenistan[a]',
                'Population': 6031200,
                'Continent': 'Asia',
                'Ref.': mocker.ANY,
            },
            2: {
                'Rank': 3,
                'Country': 'Solomon Islands',
                'Population': 686884,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            3: {
                'Rank': 4,
                'Country': 'Vanuatu',
                'Population': 307145,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            4: {
                'Rank': 5,
                'Country': 'Samoa',
                'Population': 198413,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            5: {
                'Rank': 6,
                'Country': 'Kiribati',
                'Population': 119451,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            6: {
                'Rank': 7,
                'Country': 'Micronesia',
                'Population': 115030,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            7: {
                'Rank': 8,
                'Country': 'Tonga',
                'Population': 105695,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            8: {
                'Rank': 9,
                'Country': 'Marshall Islands',
                'Population': 59190,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            9: {
                'Rank': 10,
                'Country': 'Palau',
                'Population': 18094,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            10: {
                'Rank': 11,
                'Country': 'Tuvalu',
                'Population': 11793,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
            11: {
                'Rank': 12,
                'Country': 'Nauru',
                'Population': 10823,
                'Continent': 'Oceania',
                'Ref.': mocker.ANY,
            },
        }


class TestCache:
    def _get_cache_size(self, wiki_instance):
        """Return a count of the items in the cache"""
        cache = os.path.exists(wiki_instance.cache_dir)
        if not cache:
            return 0
        _, _, cache_files = next(os.walk(wiki_instance.cache_dir))
        return len(cache_files)

    def test_cache_populated(self):
        wiki = WikiApi({'cache': True, 'cache_dir': '/tmp/wikiapi-test'})

        assert self._get_cache_size(wiki) == 0
        # Make multiple calls to ensure no duplicate cache items created
        assert wiki.find('Bob Marley') == wiki.find('Bob Marley')
        assert self._get_cache_size(wiki) == 1

        # Check cache keys are unique
        assert wiki.find('Tom Hanks') != wiki.find('Bob Marley')

        assert self._get_cache_size(wiki) == 2
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)

    def test_cache_not_populated_when_disabled(self):
        wiki = WikiApi({'cache': False})

        assert self._get_cache_size(wiki) == 0
        wiki.find('Bob Marley')
        assert self._get_cache_size(wiki) == 0
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)


class TestUnicode:
    @pytest.fixture(autouse=True)
    def set_up(self):
        # using an Italian-Emilian locale that is full of unicode symbols
        self.wiki = WikiApi({'locale': 'eml'})
        self.result = self.wiki.find('Bulaggna')[0]

    def test_search(self):
        # this is urlencoded.
        assert self.result == 'Bul%C3%A5ggna'

    def test_article(self):
        # unicode errors will likely blow in your face here
        assert self.wiki.get_article(self.result) is not None
