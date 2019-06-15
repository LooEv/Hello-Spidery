#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : seed_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-11 22:06:45
@History :
@Desc    :
"""

import scrapy.signals
from scrapy.exceptions import DontCloseSpider, CloseSpider
from scrapy.http import Request

from hello_spidery.utils.spiders.spider import HelloBaseSpider
from hello_spidery.utils.seed_provider import SeedProvider


class HelloSeedSpider(HelloBaseSpider):
    name = 'hello_seed_spider'

    def custom_init_from_crawler(self, crawler, *args, **kwargs):
        settings = crawler.settings
        seed_provider_config = settings.getdict('SEED_PROVIDER_CONFIG')
        seed_provider_config['seed_queue_name'] = self.name
        self.seed_provider = SeedProvider.from_config(**seed_provider_config)
        self.fetch_seeds_batch_size = settings.getint('FETCH_SEEDS_BATCH_SIZE', 5)
        self.close_spider_after_idle_times = settings.getint('CLOSE_SPIDER_AFTER_IDLE_TIMES', 5)
        self.spider_idle_times = 0
        self.close_reason = f'Close spider after {self.close_spider_after_idle_times} ' \
            f'times of spider idle'
        crawler.signals.connect(self.spider_idle, signal=scrapy.signals.spider_idle)

    def get_seed(self):
        try:
            return self.seed_provider.get_seed()
        except Exception:
            self.logger.exception('Fail to get seed')

    def check_is_close_spider(self):
        if self.spider_idle_times >= self.close_spider_after_idle_times:
            return True
        else:
            return False

    def make_request_from_seed(self, seed):
        raise NotImplementedError

    def spider_idle(self):
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

        if self.check_is_close_spider():
            self.crawler.engine.close_spider(self, self.close_reason)
        raise DontCloseSpider

    def next_requests(self):
        seed_found = 0
        while seed_found < self.fetch_seeds_batch_size:
            seed = self.get_seed()
            if not seed:
                break

            self.logger.info('Get seed:{}'.format(seed))
            req = self.make_request_from_seed(seed)
            if not req:
                self.logger.warning(f'Fail to make request by seed: {seed}')
                continue

            if isinstance(req, Request):
                req = [req]
            for r in req:
                if not isinstance(r, Request):
                    self.logger.warning('Non-Request object, ignore it')
                    continue
                r.meta['seed'] = seed
                yield r
            seed_found += 1

        if seed_found == 0:
            self.spider_idle_times += 1
            self.logger.info('Get empty seed ~~~, biubiubiu')
        else:
            self.spider_idle_times = 0
