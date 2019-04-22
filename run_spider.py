from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from hello_spidery.spiders.crazy_spider import CrazySpider
from hello_spidery.spiders.dianping import DianPingShop
from hello_spidery.spiders.mobile_phone_spider import MobilePhoneSpider
from hello_spidery.spiders.mobile_phone_captcha import MobilePhoneCaptcha


def run_single_spider(spider_cls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_cls)
    process.start()


def run_a_spider_multi_times():
    import time

    from twisted.internet import reactor, defer
    from scrapy.utils.log import configure_logging

    configure_logging()
    runner = CrawlerRunner()

    @defer.inlineCallbacks
    def crawl_spider():
        while 1:
            try:
                yield runner.crawl(CrazySpider)
                time.sleep(2)
            except Exception:
                reactor.stop()

    crawl_spider()
    reactor.run()


if __name__ == '__main__':
    # run_a_spider_multi_times()
    run_single_spider(MobilePhoneSpider)
