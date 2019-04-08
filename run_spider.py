from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hello_spidery.spiders.crazy_spider import CrazySpider
from hello_spidery.spiders.github import GithubSpider
from hello_spidery.spiders.meituan import MeituanBaseInfoSpider

process = CrawlerProcess(get_project_settings())

process.crawl(CrazySpider)
# process.crawl(GithubSpider)
process.start()
