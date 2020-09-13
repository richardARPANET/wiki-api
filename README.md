# wiki-api
[![Build Status](https://travis-ci.org/richardasaurus/wiki-api.png?branch=master)](https://travis-ci.org/richardasaurus/wiki-api)

A basic python library enabling access to Wikipedia.org's search results and articles.

## How To Use

### Installation

    pip install wikiapi

### Create an instance of wiki-api
```python
from wikiapi import WikiApi
wiki = WikiApi()
wiki = WikiApi({ 'locale' : 'es'}) # to specify your locale, 'en' is default
```
### Search for something on wikipedia
```python
results = wiki.find('Barack Obama') => ['Barack_Obama', 'Barack_Obama_presidential_campaign,_2008', ...]
```
### Get information about a wiki article
```python
article = wiki.get_article(results[0])

article.heading => 'Barack Obama'
article.image => 'http://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Official_portrait_of_Barack_Obama.jpg/220px-Official_portrait_of_Barack_Obama.jpg'
article.summary => 'Barack Hussein Obama II (i/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/; born August 4, 1961) is the 44th and current President of th...'
article.references => ['Obama: No green light for Israel to attack Iran. Cnn.com. 2009-07-07. http://www.cnn.com/2009/POLITICS/07/07/obama.israel.iran/. Retrieved January 4, 2013.', ..., .., ...]
article.content => 'Full article dump...'
article.url => 'http://en.wikipedia.org/wiki/Barack_Obama'
```

## Requirements

    1. Python 3
    2. See requirements.txt

## Running the tests

```
pip install tox
tox
```


