import asyncio
import time
from functools import wraps
from unittest import TestCase

from simple_proxy_pool.proxy_pool import ProxyPool
from simple_proxy_pool.spider import XiCiSpider


class TestBase(TestCase):
    def verify_url(self, url):
        self.assertRegex(url, r"http://\d+\.\d+\.\d+\.\d+:\d+")

    def verify_urls(self, urls):
        self.assertIsInstance(urls, list)
        for url in urls:
            self.verify_url(url)


def async_test(func):
    @wraps(func)
    def inner(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return inner


class TestSpider(TestBase):
    @async_test
    async def _test_spider(self, spider_cls):
        spider = spider_cls()
        urls = await spider.get_http_urls()
        self.verify_urls(urls)
        time.sleep(5)
        urls = await spider.get_https_urls()
        self.verify_urls(urls)

    def test_xici_spider(self):
        self._test_spider(XiCiSpider)


class TestProxyPool(TestBase):
    @classmethod
    def setUpClass(cls):
        cls.pl = ProxyPool()
        cls.pl.run()

    @classmethod
    def tearDownClass(cls):
        cls.pl.close()

    def setUp(self):
        timeout = 120
        step_time = 5
        total_time = 0
        while not (self.pl._http_list and self.pl._https_list):
            time.sleep(step_time)
            total_time += step_time
            self.assertLess(total_time, timeout, "Get proxy list timeout! Please check your network.")

    def test_get_one_http_url(self):
        url = self.pl.get_one_http_url()
        self.verify_url(url)

    def test_get_one_https_url(self):
        url = self.pl.get_one_https_url()
        self.verify_url(url)

    def test_get_http_urls(self):
        nums = 15
        urls = self.pl.get_http_urls(nums=nums)
        self.assertEqual(len(urls), nums)
        self.verify_urls(urls)

    def test_get_https_urls(self):
        nums = 15
        urls = self.pl.get_https_urls(nums=15)
        self.assertEqual(len(urls), nums)
        self.verify_urls(urls)
