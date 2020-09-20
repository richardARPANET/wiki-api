import hashlib
import logging
import os
import re

from xml.dom import minidom
import pandas as pd
import six
import unidecode
import requests
from bs4 import BeautifulSoup, NavigableString
from pyquery import PyQuery

logger = logging.getLogger(__name__)

uri_scheme = 'https'
api_uri = 'wikipedia.org/w/api.php'
article_uri = 'wikipedia.org/wiki/'

# common sub sections to exclude from output
UNWANTED_SECTIONS = (
    'External links and resources',
    'External links',
    'Navigation menu',
    'See also',
    'References',
    'Further reading',
    'Contents',
    'Official',
    'Other',
    'Notes',
)


class WikiApi(object):
    def __init__(self, options=None):
        if options is None:
            options = {}

        self.options = options
        if 'locale' not in options:
            self.options['locale'] = 'en'
        self.caching_enabled = True if options.get('cache') is True else False
        self.cache_dir = options.get('cache_dir') or '/tmp/wikiapicache'

    def find(self, terms):
        search_params = {
            'action': 'opensearch',
            'search': terms,
            'format': 'xml',
        }

        url = '{scheme}://{locale_sub}.{hostname_path}'.format(
            scheme=uri_scheme,
            locale_sub=self.options['locale'],
            hostname_path=api_uri,
        )
        resp = self.get(url, search_params)
        logger.debug('find "%s" response: %s', terms, resp)

        # parse search results
        xmldoc = minidom.parseString(resp)
        items = xmldoc.getElementsByTagName('Item')

        # return results as wiki page titles
        results = []
        for item in items:
            link = item.getElementsByTagName('Url')[0].firstChild.data
            slug = re.findall(r'wiki/(.+)', link, re.IGNORECASE)
            results.append(slug[0])
        return results

    def get_article(self, title):
        url = '{scheme}://{locale_sub}.{hostname_path}{article_title}'.format(
            scheme=uri_scheme,
            locale_sub=self.options['locale'],
            hostname_path=article_uri,
            article_title=title,
        )
        html = PyQuery(self.get(url))
        data = {}

        # parse wiki data
        data['heading'] = html('#firstHeading').text()
        paras = html('.mw-content-ltr').find('p')
        data['image'] = 'http:{0}'.format(
            html('body').find('.image img').attr('src')
        )
        data['summary'] = ''
        data['full'] = ''
        references = html('body').find('.references')
        data['url'] = url

        # gather references
        data['references'] = []
        for ref in references.items():
            data['references'].append(self._strip_text(ref.text()))

        # gather summary
        summary_max = 900
        chars = 0
        for pgraph in paras.items():
            if chars < summary_max:
                chars += len(pgraph.text())
                text_no_tags = self._strip_html(pgraph.outer_html())
                stripped_summary = self._strip_text(text_no_tags)
                data['summary'] += stripped_summary

        # gather full content
        for idx, line in enumerate(html('body').find('h2, p').items()):
            if idx == 0:
                data['full'] += data['heading']

            clean_text = self._strip_text(line.text())
            if clean_text:
                data['full'] += '\n\n' + clean_text

        data['full'] = self._remove_ads_from_content(data['full']).strip()
        article = Article(data)
        return article

    @staticmethod
    def _strip_html(text):  # pragma: no cover
        return BeautifulSoup(text, 'lxml').text

    def get_relevant_article(self, results, keywords):
        """
        Get the most relevant article from the results of find(),
        using a list of keywords and checking for them in article.summary
        """
        for result in results:
            article = self.get_article(result)
            summary_words = article.summary.split(' ')
            has_words = any(word in summary_words for word in keywords)
            if has_words:
                return article
        return None

    def _get_cache_item_path(self, url, params):
        """
        Generates a cache location for a given api call.
        Returns a file path
        """
        cache_dir = self.cache_dir
        m = hashlib.md5()
        hash_str = '{0}{1}'.format(six.text_type(url), six.text_type(params))
        m.update(hash_str.encode('utf-8'))
        cache_key = m.hexdigest()

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, cache_key + '.cache')

    def _get_cached_response(self, file_path):
        """ Retrieves response from cache """
        if os.path.exists(file_path):
            logger.info('retrieving from WikiApi cache: %s', file_path)

            with open(file_path, 'rb') as resp_data:
                # import pytest; pytest.set_trace()
                cached_resp = resp_data.read()

            return cached_resp

    @staticmethod
    def _cache_response(file_path, resp):
        with open(file_path, 'wb') as f:
            f.write(resp)

    def get(self, url, params={}):
        if self.caching_enabled:
            cached_item_path = self._get_cache_item_path(
                url=url, params=params
            )
            cached_resp = self._get_cached_response(cached_item_path)
            if cached_resp:
                return cached_resp

        resp = requests.get(url, params=params)
        resp_content = resp.content

        if self.caching_enabled:
            self._cache_response(cached_item_path, resp_content)

        return resp_content

    def get_tables(self, url):  # noqa: C901
        pd_tables = pd.read_html(url)
        pd_headings = []
        for table_df in pd_tables:
            try:
                table_df.columns = [
                    self._strip_text(c).strip() for c in table_df.columns
                ]
            except TypeError:
                continue
            pd_headings.append(tuple(table_df.columns))

        tables_out = {}

        soup = BeautifulSoup(self.get(url), 'html.parser')
        tables = soup.find_all('table', class_='sortable')
        if not tables:
            tables = soup.find_all('table', class_='wikitable')
        for table in tables:
            try:
                caption = table.find_all('caption')[0]
            except IndexError:
                try:
                    caption = table.find_previous('h3').text
                except AttributeError:
                    try:
                        caption = table.find_previous('h2').text
                    except AttributeError:
                        logger.info('Could not find caption for table')
                        continue
            else:
                cap_children = tuple(caption.children)
                caption = caption.text
                if cap_children:
                    children = []
                    for child in cap_children:
                        if isinstance(child, NavigableString):
                            children.append(child)
                        elif (
                            child and hasattr(child, 'text')
                            and not child.text.startswith('[')
                            and not child.find_all('abbr')
                        ):
                            children.append(child.text)
                    if children:
                        caption = (
                            ' '.join(children)
                            .replace('\n', ' ')
                            .replace(':', '')
                        )
            caption = (
                re.sub(r'\([^)]*\)', '', caption).replace(':', '').strip()
            )
            caption = self._strip_text(caption).strip()
            if not caption:
                continue
            ths = [
                t
                for t in table.find_all('th')
                if t.attrs.get('scope') == 'col'
            ]
            if not ths:
                try:
                    th = [
                        t
                        for t in table.find_all('th')
                        if 'data-sort-type' in t.attrs
                    ][0]
                except IndexError:
                    ths = table.find_all('th')
                else:
                    ths = (
                        tuple(th.previous_siblings)
                        + (th,)
                        + tuple(th.next_siblings)
                    )
                    headings = [
                        self._strip_text(x.text).strip()
                        for x in ths
                        if hasattr(x, 'text')
                    ]
                    ths2 = table.find_all('th')
                    if len(ths2) == len(headings):
                        ths = ths2
            headings = [
                self._strip_text(x.text).strip()
                for x in ths
                if hasattr(x, 'text')
            ]
            matches = tuple(
                x for x in pd_tables if x.columns.to_list() == headings
            )
            if matches:
                tables_out[caption] = matches[0]
        return tables_out

    def _strip_text(self, string):
        """Removed unwanted information from article test"""
        # remove citation numbers
        string = re.sub(r'\[\d+]', '', string)
        # correct spacing around fullstops + commas
        string = re.sub(r' +[.] +', '. ', string)
        string = re.sub(r' +[,] +', ', ', string)
        string = re.sub(r' +', ' ', string)
        # remove sub heading edits tags
        string = re.sub(r'\s*\[\s*edit\s*\]\s*', '\n', string)
        # remove unwanted areas
        string = re.sub(
            '|'.join(UNWANTED_SECTIONS), '', string, re.I | re.M | re.S
        )
        return unidecode.unidecode(string)

    @staticmethod
    def _remove_ads_from_content(bio_text):
        """Returns article content without references to Wikipedia"""
        pattern = r'([^.]*?Wikipedia[^.]*\.)'
        return re.sub(pattern, '', bio_text)


class Article(object):
    def __init__(self, data=None):
        data = data or {}
        self.heading = data.get('heading')
        self.image = data.get('image')
        self.summary = data.get('summary')
        self.content = data.get('full')
        self.references = data.get('references')
        self.url = data.get('url')

    def __repr__(self):
        return '<wikiapi.Article {0}>'.format(self.heading)
