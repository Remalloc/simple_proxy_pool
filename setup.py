from distutils.core import setup

setup(
    name="simple_proxy_pool",
    version="1.0",
    author="remalloc",
    author_email="remalloc.virtual@gmail.com",
    url="https://github.com/Remalloc/simple_proxy_pool",
    packages=["simple_proxy_pool", "unit_test"],
    install_requires=[
        "aiohttp>=3.5.4",
        "beautifulsoup4>=4.7.1",
        "lxml>=4.3.0"
    ],
    python_requires=">=3.6",
    license="BSD",
    platforms="any"
)
