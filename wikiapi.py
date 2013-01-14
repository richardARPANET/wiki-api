import requests
import urllib.parse
import re
from xml.dom import minidom
from bs4 import BeautifulSoup

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
    'Contents'
]

class WikiApi:

    def __init__( self, options={} ):
        self.options = options

        if 'locale' not in options:
            self.options['locale'] = 'en'

    def find(self, terms):
        search_params = {'action' : 'opensearch', 'search' : terms, 'format': 'xml'}
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
        global uri_scheme
        global article_uri
        url = uri_scheme + '://' + self.options['locale'] + '.' + article_uri + title
        html = BeautifulSoup(self.get(url))
        data = dict()

        #parse wiki data
        data['heading'] = html.find(id='firstHeading').text
        paras = html.find(class_='mw-content-ltr').find_all('p')
        data['image'] = 'http:' + html.find(class_='image').find('img')['src']
        data['summary'] = str()
        data['full'] = str()
        references = html.find_all(class_='web')

        #gather references
        data['references'] = []
        for ref in references:
            data['references'].append(self.strip_text(ref.text))

        #gather summary
        summary_max = 900
        chars = 0
        for p in paras:
            if chars < summary_max:
                chars += len(p.text)
                data['summary'] += '\n\n' + self.strip_text(p.text)

        #gather full content
        i = 0
        for line in html.find(id='firstHeading').find_all_next(['h2','p']):
            #wiki heading
            if i == 0:
                data['full'] += data['heading']
            #rest of the article
            data['full'] += '\n\n' + self.strip_text(line.text)
            i += 1

        article = Article(data)
        return article

    def build_url(self, params, locale='en'):
        global api_uri
        global uri_scheme
        default_params = {'format' : 'xml'}
        query_params = dict(list(default_params.items()) + list(params.items()))
        query_params = urllib.parse.urlencode(query_params)
        return uri_scheme + '://' + self.options['locale'] + '.' + api_uri + '?' + query_params

    def get(self, url):
        r = requests.get(url)
        return r.text

    # remove unwanted information
    def strip_text(self, string):
        #remove cite no.s
        string = re.sub(r'\[\d+\]', '', string)
        #remove wiki text bold markup
        string = re.sub(r'"', '', string)
        #remove sub heading edits tags
        string = re.sub(r'\[edit\]\s', '\n', string)
        #remove unwanted areas
        string = re.sub("|".join(unwanted_sections),'', string, re.IGNORECASE)
        return string

class Article:
    def __init__( self, data={}):
        self.heading = data['heading']
        self.image = data['image']
        self.summary = data['summary']
        self.content = data['full']
        self.references = data['references']