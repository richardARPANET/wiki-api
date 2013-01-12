from wikiapi import  WikiApi()

wiki = WikiApi()
results = wiki.find('Barack Obama')
article = wiki.get_article(results[0]) #taking first search result

def do_test():
    print(article.heading) #wiki article main heading
    print(article.image) #article image
    print(article.summary) #short summary text
    print(article.references) #array of references
    print(article.content) #full article content

if __name__ == '__main__':
    do_test()