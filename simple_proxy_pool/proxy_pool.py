import aiohttp
import asyncio
import time
from multiprocessing import Process, Manager
from random import choice, choices

from simple_proxy_pool.config import REQUEST_HEADERS
from simple_proxy_pool.logger import root_logger, set_logger_config
from simple_proxy_pool.spider import XiCiSpider, Spider


class ProxyPool(object):
    def __init__(self, total: int = 10, proxy_timeout: int = 3, crawl_interval: int = 40
                 , log_config: dict = None):
        """
        Create proxy pool and set params for pool, and then call run() function to start this pool.
        :param total: Maximum connections in pool. Note: It's approximately number.
        :param proxy_timeout: Test proxy connection timeout. If set lower value, the delay also lowered.
        :param crawl_interval: Two crawl intervals. If set too low could cause unable to access website.
        :param log_config: Custom log config. Default config is in the logger.py.
        """
        self.total = total
        self.proxy_timeout = aiohttp.ClientTimeout(total=proxy_timeout)
        self.crawl_interval = crawl_interval
        # Test proxy connection website, suggest set what you want to proxy to access website.
        self.test_http_web = "http://www.zhihu.com"
        self.test_https_web = "https://www.zhihu.com"
        self._spiders = [XiCiSpider()]
        self._manager = Manager()
        self._http_list = self._manager.list()
        self._https_list = self._manager.list()
        if log_config:
            set_logger_config(log_config)
        self._process = None

    async def _filter_urls(self, urls: list, is_https: bool = False) -> list:
        """
        Filter can't use proxy connections.
        :param urls: The proxy URLs list. Example: ["http://1234:9090","https://1234:9090"]
        :param is_https: True or False, default False.
        This will determine whether to test the connection using the HTTPS protocol.
        :return: Filtered URLs.
        """

        async def verify_proxy(proxy_url: str):
            """
            Verify proxy connection can be connected.
            :param proxy_url: If protocol is "https" will access self.test_https_web,
            otherwise access self.test_http_web.
            :return: Only test website response status equal 200 will return url, otherwise return None.
            """
            try:
                async with aiohttp.ClientSession(headers=REQUEST_HEADERS, timeout=self.proxy_timeout) as session:
                    if is_https:
                        async with session.get(self.test_https_web, proxy=proxy_url) as resp:
                            return proxy_url if resp.status == 200 else None
                    else:
                        async with session.get(self.test_http_web, proxy=proxy_url) as resp:
                            return proxy_url if resp.status == 200 else None
            except (asyncio.TimeoutError, aiohttp.ClientError):
                pass
            except Exception as e:
                root_logger.warning(e)

        tasks = (asyncio.ensure_future(verify_proxy(url)) for url in urls)
        result = await asyncio.gather(*tasks)
        return list(filter(lambda r: r, result))

    async def acquire_url_list(self):
        """Acquire proxy list from spider websites and add to http list or https list."""
        for spider in self._spiders:
            if len(self._http_list) < self.total:
                all_urls = await spider.get_http_urls()
                urls = await self._filter_urls(all_urls, is_https=False)
                self._http_list.extend(urls)
            if len(self._https_list) < self.total:
                all_urls = await spider.get_https_urls()
                urls = await self._filter_urls(all_urls, is_https=True)
                self._https_list.extend(urls)

    async def main(self):
        """
        Timing filtering proxy list and acquire list from spider website
        when http list or https list less than self.total.
        """
        while True:
            if len(self._https_list) < self.total or len(self._https_list) < self.total:
                await self.acquire_url_list()
            else:
                self._http_list = await self._filter_urls(self._http_list)
                self._https_list = await self._filter_urls(self._https_list)
            time.sleep(self.crawl_interval)

    def set_spiders(self, spiders: list):
        """
        The spider must inherit 'Spider' class.
        :param spiders: Spider instance list. Example:[XiCiSpider(param)...]
        """
        for spider in spiders:
            assert isinstance(spider, Spider), "The spider must inherit 'Spider' class!"
        self._spiders = spiders

    def get_http_urls(self, nums: int = 0) -> list:
        """
        Choice a number of http urls.
        :param nums: The number of urls what you want to use.If nums is 0, will return all proxies.
        Note: If nums greater than current list size then maybe get repeat url.
        :return: Http proxy list.
        """
        temp_list = self._http_list[:]
        if nums > len(temp_list) and nums > 0:
            extra_list = choices(temp_list, k=nums - len(temp_list))
            temp_list.extend(extra_list)
            return temp_list
        else:
            return temp_list[:nums]

    def get_one_http_url(self) -> str:
        """
        Random choice one http url.
        :return: One http proxy.
        """
        return choice(self._http_list) if self._http_list else None

    def get_https_urls(self, nums: int = 0) -> list:
        """
        Choice a number of https urls.
        :param nums: The number of urls what you want to use.
        Note: If nums greater than current list size then maybe get repeat url.If nums is 0, will return all proxies.
        :return: Https proxy list.
        """
        temp_list = self._https_list[:]
        if nums > len(temp_list) and nums > 0:
            extra_list = choices(temp_list, k=nums - len(temp_list))
            temp_list.extend(extra_list)
            return temp_list
        else:
            return temp_list[:nums]

    def get_one_https_url(self) -> str:
        """
        Random choice one https url.
        :return: One https proxy.
        """
        return choice(self._https_list) if self._https_list else None

    def run(self):
        """Start proxy pool by daemon process"""

        def start_loop():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.main())

        self._process = Process(target=start_loop)
        self._process.daemon = True
        self._process.start()

    def close(self):
        """Close proxy pool if that running"""
        if self._process:
            self._process.terminate()
            # Clean http and https list.
            self._https_list[:] = []
            self._http_list[:] = []


def main():
    """
    Default start pool way, output ip to root logger.
    Note: It will block current process.
    """
    pl = ProxyPool()
    pl.run()
    while True:
        http = pl.get_one_http_url()
        if http:
            root_logger.info(f"http,{http}")
        https = pl.get_one_https_url()
        if https:
            root_logger.info(f"https,{https}")
        time.sleep(30)


if __name__ == '__main__':
    main()
