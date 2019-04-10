#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : crazy_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-01 11:41:22
@History :
@Desc    :
"""

import attr

from scrapy.loader import ItemLoader
from scrapy.spiders import Spider, CrawlSpider
from scrapy.http import Request, FormRequest

from hello_spidery.items.parse_item import ParsedItem
from hello_spidery.downloadermiddlewares.keyword_filter import KeywordCheckScopeEnum, \
    KeywordCheckMethodEnum

@attr.s
class Cookie:
    host = attr.ib()
    port = attr.ib()

    def get_cookie(self):
        # return []
        return {'host': self.host, 'port': self.port}


class CrazySpider(Spider):
    name = 'crazy_spider'

    custom_settings = {
        'USE_DEFAULT_ERROR_BACK': True,

        # 'INJECT_COOKIE_BY_MW': True,
        'COOKIE_PROVIDER': {'class': Cookie, 'args': ('threehao.com', '6868'), 'kwargs': {}},

        'KEYWORD_FILTER': [
            {
                'keyword': 'test',
                'check_method': KeywordCheckMethodEnum.IN_CHECKING,
                'check_scope': KeywordCheckScopeEnum.BODY,
                'allow': False,
                'change_proxy': True,
            },
        ]
    }

    # start_urls = [
    #     'http://httpbin.org/status/500'
    # ]

    def start_requests(self):
        # yield Request('http://httpbin.org/status/500', dont_filter=True, callback=self.parse)
        yield Request('http://httpbin.org/headers', dont_filter=True, callback=self.parse)

    def parse(self, response):
        print(response.text)
        yield Request('http://httpbin.org/cookies', callback=self.parse_header, meta={'inject_cookie_by_mw': True})
        yield Request('http://httpbin.org/cookies', callback=self.parse_header, dont_filter=True)

    def parse_header(self, response):
        self.logger.info(response.text)
        # title = response.xpath('//title').extract()[0]
        item = ParsedItem()
        item['version'] = 'abc'
        yield item
