# Simple Proxy Pool
免费、简单、灵活的代理连接池
## 安装与卸载
[安装包下载](https://github.com/Remalloc/simple_proxy_pool/releases/download/v1.0/simple_proxy_pool-1.0.tar.gz) 或 `clone git@github.com:Remalloc/simple_proxy_pool.git`<br>
```
# 需要pip和setuptools
# 进入程序目录安装
python setup.py install
# 卸载
pip uninstall simple-proxy-pool
```
## 快速开始
```python
import time
from simple_proxy_pool.proxy_pool import ProxyPool

pl = ProxyPool()
pl.test_http_web = "http://www.baidu.com"  # 同一个代理访问不同的网站速度是不相同的,建议设置成想要访问的网站,默认是知乎官网
pl.test_https_web = "https://www.baidu.com"
pl.run()
time.sleep(60) # 初次启动可能没有可以使用的代理,需要等待一段时间
http = pl.get_one_http_url()
if http:
    print(http)
    # 可以使用http代理
https = pl.get_one_https_url()
if https:
    print(https)
    # 可以使用https代理

# -----更好的嵌入代码------
def get_http_proxy():
    while True:
        url = pl.get_one_http_url()
        if url:
            return url
        else:
            time.sleep(5)
```
### 注意
* 每次获取的代理地址有可能相同也有可能不同,需要使用者自行判断
* 因为免费代理存在时效性和不稳定性,所以尽量不要存储地址一直使用,代理池大约每40秒过滤一次地址,保证连接畅通.
* 取出的连接不能保证一定能使用,注意做异常处理

## API
```python

class ProxyPool(object):
    def __init__(self, total: int = 10, proxy_timeout: int = 3, crawl_interval: int = 40
                 , log_config: dict = None):
        """
        初始化连接池,使用run函数运行连接池
        :param total: 设置连接池的最大连接数.这个是估计值,开始运行时可能小于这个值,运行一段时间后也可能略大于这个值
        :param proxy_timeout: 代理超时时间,越小表示筛选出的连接速度越快,但是会导致可用连接变少.
        :param crawl_interval: 两次爬虫时间间隔,当连接池连接数小于设置值时,会启动爬虫.数值过小可能会导致IP被封.
        :param log_config: 自定义日志输出方式,参照logger.py
        """
        pass

    async def _filter_urls(self, urls: list, is_https: bool = False) -> list:
        """
        过滤代理连接列表,清除不可用连接
        :param urls: 代理列表. 例如: ["http://1234:9090","https://1234:9090"]
        :param is_https: True或False,默认False.这将决定是否使用HTTPS协议测试连接
        :return: 过滤后的列表
        """
        pass

    async def acquire_url_list(self):
        """用爬虫获取代理列表,并过滤列表."""
        pass

    async def main(self):
        """
        定时过滤当前代理地址,当可用连接数小于self.total时启用爬虫获取.
        """
        pass

    def set_spiders(self, spiders: list):
        """
        设置爬虫列表,其中每个实例都应该继承spider.py中的Spider类
        :param spiders: 爬虫实例列表. 例如:[XiCiSpider(param)...]
        """
        pass

    def get_http_urls(self, nums: int = 0) -> list:
        """
        获取一定数量的代理.
        :param nums: 代理数量.如果为0将会返回全部可用代理.
        注意: 如果代理数量超过当前代理列表大小,可能会返回重复的代理.
        :return: 可用于HTTP协议的代理列表.
        """
        pass

    def get_one_http_url(self) -> str:
        """
        随机返回一个代理.
        :return: 一个可用于HTTP协议的代理.
        """
        pass

    def get_https_urls(self, nums: int = 0) -> list:
        """
        获取一定数量的代理.
        :param nums: 代理数量.如果为0将会返回全部可用代理.
        注意: 如果代理数量超过当前代理列表大小,可能会返回重复的代理.
        :return: 可用于HTTPS协议的代理列表.
        """
        pass

    def get_one_https_url(self) -> str:
        """
        随机返回一个代理.
        :return: 一个可用于HTTP协议的代理.
        """
        pass

    def run(self):
        """开启代理连接池,会为当前进程启动一个守护进程,主进程结束时自动结束"""
        pass

    def close(self):
        """关闭代理连接池并清空代理列表,如果连接池已开启"""
        pass
```
## 扩展
本程序可以很方便的定制自己所需要的功能,下面具体介绍几种场景.
#### 独立使用连接池
可以直接将连接池作为单独模块使用,只需要主进程定时从池中取出连接存入数据库,或者变为使用API提取
#### 扩展爬虫IP列表
spider模块提供了一个抽象类和一个方法类,只需要实现抽象类中的方法即可被代理池使用<br>
```python
class AsyncBaseOperation(object):
    """封装了aiohttp的基础操作,简化请求操作,可选继承"""

    @staticmethod
    async def fetch(session, url: str, proxies: list = None):
        """
        使用已存在的会话访问网页
        :param session: 会话对象aiohttp.ClientSession.
        :param url: 网页地址.
        :param proxies: 代理列表,默认不使用代理,如果提供会从中随机选择一个代理使用.
        :return: 网页内容.
        """
        pass

    @staticmethod
    async def get(url, proxies: list = None):
        """
        创建一个会话并访问网页
        :param url: 网页地址.
        :param proxies: 代理列表,默认不使用代理,如果提供会从中随机选择一个代理使用.
        :return: 网页内容.
        """
        pass
        
class Spider:
    """所有爬虫类必须继承此类"""

    def get_http_urls(self) -> list:
        """返回http代理列表,例如: ["http://1.2.3.4:56"]"""
        pass

    def get_https_urls(self) -> list:
        """返回http代理列表,例如: ["http://1.2.3.4:56"]"""
        pass
```
**注意!!:使用新的爬虫类时需要在连接池启动前用set_spiders函数设置爬虫列表**
## 测试
直接运行proxy_pool.py可以进行简单的测试,会不时的将可用的地址打印出来.
<br>
如果你想运行单元测试可以直接运行unit_test目录下的test.py,如果你扩展了spider强烈建议你将其加入到单元测试中,
并且你只需要在TestSpider中添加两行代码即可:
```python
from simple_proxy_pool.spider import NewSpider
class TestSpider(TestBase):
    #...
    def test_new_spider(self):
        self._test_spider(NewSpider)
```
## 关于
* 本项目使用BSD开源协议
* 目前还需要完善筛选逻辑和部分文档,欢迎提交PR共同开发
* 如有问题或建议可提交issue或联系remalloc.virtual@gmail.com
