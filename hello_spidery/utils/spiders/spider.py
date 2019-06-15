#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-22 15:38:35
@History :
@Desc    : 
"""

import time
from scrapy.spiders import Spider

from hello_spidery.items.parsed_item import ParsedItem
from hello_spidery.utils.commons import calc_str_md5, seconds_2_str


class HelloBaseSpider(Spider):
    name = 'hello_base_spider'
    data_version = 'v1.0'

    custom_settings = {'USE_DEFAULT_ERROR_BACK': True}

    # 如果需求使用额外的scrapy支持的配置，请放置在 specific_settings 中
    # waring: 切记不要轻易覆盖 custom_settings
    specific_settings = {}

    def assemble_parsed_item(self, response, _id=None):
        item = ParsedItem()
        item['_id'] = _id or calc_str_md5(response.url)
        item['update_time'] = int(time.time())
        item['do_time'] = seconds_2_str()
        item['version'] = self.data_version
        item['_html'] = ''
        item['_request_url'] = response.url
        item['_request_method'] = response.request.method
        item['_request_params'] = response.request.body[:500]
        return item

    def custom_init_from_crawler(self, crawler, *args, **kwargs):
        pass

    def custom_init(self, *args, **kwargs):
        pass  # you can init something yourself here

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(HelloBaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.custom_init_from_crawler(crawler, *args, **kwargs)
        spider.custom_init(*args, **kwargs)
        return spider

    @classmethod
    def update_settings(cls, settings):
        cls.custom_settings.update(cls.specific_settings)
        super(HelloBaseSpider, cls).update_settings(settings)


HelloSpider = HelloBaseSpider
