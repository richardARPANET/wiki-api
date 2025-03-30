# -*- coding: utf-8 -*-
import os
import shutil

import pytest
from six.moves import urllib_parse
from wikiapi import WikiApi


def assert_url_valid(url):
    if not bool(urllib_parse.urlparse(url).netloc):
        raise AssertionError(f"{url} is not a valid URL")


class TestWiki:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.wiki = WikiApi()
        self.results = self.wiki.find("Bill Clinton")
        self.article = self.wiki.get_article(self.results[0])

    def test_heading(self):
        assert self.article.heading == "Bill Clinton"

    def test_image(self):
        assert_url_valid(url=self.article.image)

    def test_summary(self):
        results = self.wiki.find("Tom Hanks")
        article = self.wiki.get_article(results[0])

        assert "Thomas" in article.summary
        assert "Jeffrey" in article.summary
        assert "Hanks" in article.summary

    def test_content(self):
        assert len(self.article.content) > 200

    def test_references(self):
        assert isinstance(self.article.references, list) is True

    def test_url(self):
        assert_url_valid(url=self.article.url)
        assert self.article.url == "https://en.wikipedia.org/wiki/Bill_Clinton"

    def test_get_relevant_article(self):
        keywords = ["president", "hilary"]
        _article = self.wiki.get_relevant_article(self.results, keywords)

        assert "Bill Clinton" in _article.heading
        assert len(_article.content) > 5000
        assert "President Bill Clinton" in _article.content

    def test_get_relevant_article_no_result(self):
        keywords = ["hockey player"]
        _article = self.wiki.get_relevant_article(self.results, keywords)
        assert _article is None

    def test__remove_ads_from_content(self):
        content = (
            "From Wikipedia, the free encyclopedia. \n\nLee Strasberg "
            "(November 17, 1901 2013 February 17, 1982) was an American "
            "actor, director and acting teacher.\n"
            "Today, Ellen Burstyn, Al Pacino, and Harvey Keitel lead this "
            "nonprofit studio dedicated to the development of actors, "
            "playwrights, and directors.\n\nDescription above from the "
            "Wikipedia article\xa0Lee Strasberg,\xa0licensed under CC-BY-SA, "
            "full list of contributors on Wikipedia."
        )

        result_content = self.wiki._remove_ads_from_content(content)

        expected_content = (
            " \n\nLee Strasberg "
            "(November 17, 1901 2013 February 17, 1982) was an American "
            "actor, director and acting teacher.\n"
            "Today, Ellen Burstyn, Al Pacino, and Harvey Keitel lead this "
            "nonprofit studio dedicated to the development of actors, "
            "playwrights, and directors."
        )
        assert expected_content == result_content

    @pytest.mark.parametrize(
        "url, expected_tables",
        [
            (
                "https://en.wikipedia.org/wiki/Chess_Classic",
                [
                    "Chess Classic Championship",
                    "Rapid Chess Open",
                    "Chess960 Rapid chess World Championship",
                    "FiNet Open Chess960",
                    "Chess960 Computer World Championship",
                ],
            ),
            (
                "https://en.wikipedia.org/wiki/List_of_missions_to_the_Moon",
                [
                    "20th century",
                    "21st century",
                    "Mission milestones by country",
                    "Analysis of numbers of lunar missions",
                    "Funded and are under development",
                    "Proposed but full funding still unclear",
                    "Lunar Rovers",
                ],
            ),
            (
                "https://en.wikipedia.org/wiki/"
                "List_of_people_who_have_walked_on_the_Moon",
                [
                    "Apollo astronauts who walked on the Moon",
                    "Apollo astronauts who flew to the Moon without landing",
                    "Astronauts who died during the Apollo Program",
                ],
            ),
        ],
    )
    def test_get_tables_returns_expected_keys(self, url, expected_tables):
        tables = self.wiki.get_tables(url=url)

        assert set(tables.keys()) == set(expected_tables)

    def test_get_tables(self, mocker):
        url = (
            "https://en.wikipedia.org/wiki/"
            "COVID-19_pandemic_by_country_and_territory"
        )

        tables = self.wiki.get_tables(url=url)

        assert tables
        assert isinstance(tables, dict)
        assert tuple(tables.keys())
        assert (
            len(
                tables[
                    "COVID-19 cases, deaths, and rates by location"
                ].T.to_dict()
            )
            > 2
        )


class TestCache:
    def _get_cache_size(self, wiki_instance):
        """Return a count of the items in the cache"""
        cache = os.path.exists(wiki_instance.cache_dir)
        if not cache:
            return 0
        _, _, cache_files = next(os.walk(wiki_instance.cache_dir))
        return len(cache_files)

    def test_cache_populated(self):
        wiki = WikiApi({"cache": True, "cache_dir": "/tmp/wikiapi-test"})

        assert self._get_cache_size(wiki) == 0
        # Make multiple calls to ensure no duplicate cache items created
        assert wiki.find("Bob Marley") == wiki.find("Bob Marley")
        assert self._get_cache_size(wiki) == 1

        # Check cache keys are unique
        assert wiki.find("Tom Hanks") != wiki.find("Bob Marley")

        assert self._get_cache_size(wiki) == 2
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)

    def test_cache_not_populated_when_disabled(self):
        wiki = WikiApi({"cache": False})

        assert self._get_cache_size(wiki) == 0
        wiki.find("Bob Marley")
        assert self._get_cache_size(wiki) == 0
        shutil.rmtree(wiki.cache_dir, ignore_errors=True)


class TestUnicode:
    @pytest.fixture(autouse=True)
    def set_up(self):
        # using an Italian-Emilian locale that is full of unicode symbols
        self.wiki = WikiApi({"locale": "eml"})
        self.result = self.wiki.find("Bulaggna")[0]

    def test_search(self):
        # this is urlencoded.
        assert self.result == "Bul%C3%A5ggna"

    def test_article(self):
        # unicode errors will likely blow in your face here
        assert self.wiki.get_article(self.result) is not None
