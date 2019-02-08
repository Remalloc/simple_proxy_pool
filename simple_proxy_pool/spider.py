import aiohttp
from abc import ABCMeta, abstractmethod
from random import choice

from bs4 import BeautifulSoup

from simple_proxy_pool.config import REQUEST_HEADERS
from simple_proxy_pool.logger import root_logger


class AsyncBaseOperation(object):
    """Packaging aiohttp functions"""

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, url: str, proxies: list = None):
        """
        Using existing session fetches website content.
        :param session: Client session.
        :param url: Website url.
        :param proxies: Random choice proxy from this list.
        :return: Website text.
        """
        proxy = choice(proxies) if proxies else None
        async with session.get(url, proxy=proxy) as response:
            return await response.text()

    @staticmethod
    async def get(url, proxies: list = None):
        """
        Create a session and fetch website content.
        :param url: Website url.
        :param proxies: Random choice proxy from this list.
        :return: Website text.
        """
        default_timeout = aiohttp.ClientTimeout(total=6)
        async with aiohttp.ClientSession(headers=REQUEST_HEADERS, timeout=default_timeout) as session:
            return await AsyncBaseOperation.fetch(session, url, proxies)


class Spider(metaclass=ABCMeta):
    """All spiders must inherit this class"""

    @abstractmethod
    def get_http_urls(self) -> list:
        """
        Return url which is starts with 'http ://' and used for http protocol.
        Example: ["http://1.2.3.4:56"]
        """
        pass

    @abstractmethod
    def get_https_urls(self) -> list:
        """
        Return url which is starts with 'http ://' and used for https protocol.
        Example: ["http://1.2.3.4:56"]
        """
        pass


class XiCiSpider(Spider, AsyncBaseOperation):
    def __init__(self, proxies: list = None):
        """
        :param proxies: The spider random choice one if provide more than one proxy.
        Note: Make sure you provide stable proxy address.
        """
        super().__init__()
        self.http_urls = tuple(f"https://www.xicidaili.com/wt/{idx}" for idx in range(10))
        self.https_urls = tuple(f"https://www.xicidaili.com/wn/{idx}" for idx in range(10))
        self.proxies = proxies

    @property
    def http_url(self) -> str:
        return choice(self.http_urls)

    @property
    def https_url(self) -> str:
        return choice(self.https_urls)

    async def _parse_html_get_urls(self, url) -> list:
        """
        Parse website and extract proxy list.
        :param url: Target website.
        :return: Proxy list.
        """
        try:
            text = await self.get(url, self.proxies)
            soup = BeautifulSoup(text, "lxml")
            all_tr = soup.find("table", id="ip_list").find_all("tr")[1:]
            urls = [f"http://{tr.find_all('td')[1].string}:{tr.find_all('td')[2].string}" for tr in all_tr]
            return urls
        except Exception as e:
            root_logger.warning(e)
            return []

    async def get_http_urls(self) -> list:
        urls = await self._parse_html_get_urls(self.http_url)
        return urls

    async def get_https_urls(self) -> list:
        urls = await self._parse_html_get_urls(self.https_url)
        return urls
