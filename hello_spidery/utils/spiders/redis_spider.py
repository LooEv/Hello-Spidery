#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : redis_spider.py
@Version : v1.0
@Time    : 2019-06-11 14:15:49
@History :
@Desc    : 
"""

from scrapy.http import Request
from scrapy.exceptions import DontCloseSpider
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider

from .spider import HelloBaseSpider


class HelloRedisSpider(HelloBaseSpider, RedisSpider):
    custom_settings = dict(
        USE_DEFAULT_ERROR_BACK=True,
        SCHEDULER="scrapy_redis.scheduler.Scheduler",
        DUPEFILTER_CLASS="scrapy_redis.dupefilter.RFPDupeFilter",

        # 默认不使用 scrapy-redis 自带的pipeline
        # ITEM_PIPELINES={
        #     'scrapy_redis.pipelines.RedisPipeline': 300
        # },
    )

    def custom_init_from_crawler(self, crawler, *args, **kwargs):
        settings = crawler.settings
        self.close_spider_after_idle_times = settings.getint('CLOSE_SPIDER_AFTER_IDLE_TIMES', 10)
        self.spider_idle_times = 0
        self.close_reason = f'Close spider after {self.close_spider_after_idle_times} ' \
            f'times of spider idle'

    def check_is_close_spider(self):
        if self.spider_idle_times >= self.close_spider_after_idle_times:
            return True
        else:
            return False

    def spider_idle(self):
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

        if self.check_is_close_spider():
            self.crawler.engine.close_spider(self, self.close_reason)
        raise DontCloseSpider

    def push_data(self, data: str):
        try:
            use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
            push_one = self.server.sadd if use_set else self.server.rpush
            push_one(self.redis_key, data.encode())
        except Exception:
            self.logger.exception('fail to push data: ')

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                # Queue empty.
                break

            self.logger.info('Get seed:{}'.format(data))
            req = self.make_request_from_data(data)
            if not req:
                self.logger.warning("Request not made from data: %r", data)
                continue

            if isinstance(req, Request):
                req = [req]
            for r in req:
                if not isinstance(r, Request):
                    self.logger.warning('Non-Request object, ignore it')
                    continue
                r.meta['seed'] = data.decode()
                yield r
            found += 1

        if found == 0:
            self.spider_idle_times += 1
            self.logger.info('Get empty seed ~~~, biubiubiu')
        else:
            self.spider_idle_times = 0
            self.logger.info("Read %s requests from '%s'", found, self.redis_key)
