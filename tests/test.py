from wikiapi import WikiApi
import unittest

wiki = WikiApi({})
results = wiki.find('Bill Clinton')
article = wiki.get_article(results[0])  # taking first search result


class TestWiki(unittest.TestCase):
    def test_heading(self):
        self.assertIsNotNone(article.heading)

    def test_image(self):
        self.assertTrue(isinstance(article.image, str))

    def test_summary(self):
        self.assertGreater(len(article.summary), 100)

    def test_content(self):
        self.assertGreater(len(article.content), 200)

    def test_references(self):
        self.assertTrue(isinstance(article.references, list))


if __name__ == '__main__':
    unittest.main()