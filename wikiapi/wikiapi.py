from xml.dom import minidom
from pyquery import PyQuery
import requests
import urllib
import re

uri_scheme = 'http'
api_uri = 'wikipedia.org/w/api.php'
article_uri = 'wikipedia.org/wiki/'

#common sub sections to exclude from output
unwanted_sections = [
    'External links',
    'Navigation menu',
    'See also',
    'References',
    'Further reading',
    'Contents',
    'Official',
    'Other',
    'Notes',
]


class WikiApi:

    def __init__(self, options=None):
        if options is None:
            options = {}

        self.options = options
        if 'locale' not in options:
            self.options['locale'] = 'en'

    def find(self, terms):
        search_params = {'action': 'opensearch',
                         'search': terms,
                         'format': 'xml'}
        url = self.build_url(search_params)
        resp = self.get(url)

        #parse search results
        xmldoc = minidom.parseString(resp)
        items = xmldoc.getElementsByTagName('Item')

        #return results as wiki page titles
        results = []
        for item in items:
            link = item.getElementsByTagName('Url')[0].firstChild.data
            slug = re.findall(r'wiki/(.+)', link, re.IGNORECASE)
            results.append(slug[0])
        return results

    def get_article(self, title):
        url = '{0}://{1}.{2}{3}'.format(
            uri_scheme, self.options['locale'], article_uri, title)
        html = PyQuery(self.get(url))
        data = dict()

        # parse wiki data
        data['heading'] = html('#firstHeading').text()
        paras = html('.mw-content-ltr').find('p')
        data['image'] = 'http:{0}'.format(
            html('body').find('.image img').attr('src'))
        data['summary'] = str()
        data['full'] = unicode()
        references = html('body').find('.web')
        data['url'] = url

        # gather references
        data['references'] = []
        for ref in references.items():
            data['references'].append(self.strip_text(ref.text()))

        # gather summary
        summary_max = 900
        chars = 0
        for p in paras.items():
            if chars < summary_max:
                chars += len(p.text())
                data['summary'] += '\n\n' + self.strip_text(p.text())

        # gather full content
        for idx, line in enumerate(html('body').find('h2, p').items()):
            if idx == 0:
                data['full'] += data['heading']

            clean_text = self.strip_text(line.text())
            if clean_text:
                data['full'] += '\n\n' + clean_text

        data['full'] = data['full'].strip()
        article = Article(data)
        return article

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

    def build_url(self, params):
        default_params = {'format': 'xml'}
        query_params = dict(
            list(default_params.items()) + list(params.items()))
        query_params = urllib.urlencode(query_params)
        return '{0}://{1}.{2}?{3}'.format(
            uri_scheme, self.options['locale'], api_uri, query_params)

    def get(self, url):
        r = requests.get(url)
        return r.content

    # remove unwanted information
    def strip_text(self, string):
        #remove citation numbers
        string = re.sub(r'\[\s\d+\s\]', '', string)
        #remove wiki text bold markup tags
        string = re.sub(r'"', '', string)
        #correct spacing around fullstops + commas
        string = re.sub(r' +[.] +', '. ', string)
        string = re.sub(r' +[,] +', ', ', string)
        #remove sub heading edits tags
        string = re.sub(r'\s*\[\s*edit\s*\]\s*', '\n', string)
        #remove unwanted areas
        string = re.sub("|".join(unwanted_sections), '', string, re.IGNORECASE)
        return string


class Article:
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.heading = data.get('heading')
        self.image = data.get('image')
        self.summary = data.get('summary')
        self.content = data.get('full')
        self.references = data.get('references')
        self.url = data.get('url')

    def __repr__(self):
        return '<wikiapi.Article {0}>'.format(self.heading)
