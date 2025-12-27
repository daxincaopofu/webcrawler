import unittest
from crawl import normalize_url

class TestCrawl(unittest.TestCase):
    def test_normalize_url_1(self):
        self.assertEqual(normalize_url("https://blog.boot.dev/path/"), "blog.boot.dev/path")

    def test_normalize_url_2(self):
        self.assertEqual(normalize_url("https://blog.boot.dev/path"), "blog.boot.dev/path")

    def test_normalize_url_3(self):
        self.assertEqual(normalize_url("http://blog.boot.dev/path/"), "blog.boot.dev/path")

    def test_normalize_url_4(self):
        self.assertEqual(normalize_url("http://blog.boot.dev/path"), "blog.boot.dev/path")

if __name__ == "__main__":
    unittest.main()