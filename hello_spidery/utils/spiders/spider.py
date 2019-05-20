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

    def assemble_parsed_item(self, response, _id=None):
        item = ParsedItem()
        item['_id'] = _id or calc_str_md5(response.url)
        item['update_time'] = int(time.time())
        item['do_time'] = seconds_2_str()
        item['version'] = self.data_version
        item['_html'] = ''
        item['_request_url'] = response.url
        item['_request_method'] = response.request.method
        item['_request_params'] = response.request.body
        return item
