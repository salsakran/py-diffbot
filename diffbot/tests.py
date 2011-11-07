#!/usr/bin/env python

import unittest

from diffbot import DiffBot
from handlers import HttpHandler
from cache import CacheHandler

class DiffBotTest(unittest.TestCase):

    def setUp(self):
        self.diffbot = DiffBot() # dev_key has to come from the environment (DIFFBOT_KEY)
        self.test_url = 'http://nomulous.com/'
        self.test_url_id = self.diffbot.follow_add(self.test_url)['id']

    def test_http_handler_instance(self):
        self.assertIsInstance(self.diffbot.http_handler(), HttpHandler)

    def test_cache_handler_instance(self):
        self.assertIsInstance(self.diffbot.http_handler().cache_handler(), CacheHandler)

    def test_article_API(self):
        article_info = self.diffbot.article(self.test_url)

        self.assertIsInstance(article_info, dict)
        self.assertNotEqual(len(article_info), 0)

        for key in ['url', 'text', 'xpath', 'tags', 'raw_response', 'title']:
            self.assertTrue(article_info.has_key(key))

    def test_follow_add_API(self):
        follow_add_info = self.diffbot.follow_add(self.test_url)

        self.assertIsInstance(follow_add_info, dict)
        self.assertNotEqual(len(follow_add_info), 0)

        for key in ['id', 'pubDate', 'title']:
            self.assertTrue(follow_add_info.has_key(key))


    def test_follow_read_API(self):
        follow_read_info = self.diffbot.follow_read(self.test_url_id)

        self.assertIsInstance(follow_read_info, dict)
        self.assertNotEqual(len(follow_read_info), 0)

        for key in ['info', 'items']:
            self.assertTrue(follow_read_info.has_key(key))




if __name__ == '__main__':
    unittest.main()