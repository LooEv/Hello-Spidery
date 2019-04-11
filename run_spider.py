from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hello_spidery.spiders.crazy_spider import CrazySpider
from hello_spidery.spiders.dianping import DianPingShop

process = CrawlerProcess(get_project_settings())

process.crawl(DianPingShop)
process.start()
