#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : file_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-25 19:46:20
@History :
@Desc    :
"""

import os

from scrapy import Item, Field

from hello_spidery.utils.spiders import HelloBaseSpider


class MyFileItem(Item):
    file_urls = Field()
    files = Field()


class MyFileSpider(HelloBaseSpider):
    start_urls = ['http://www.innocom.gov.cn/gxjsqyrdw/dfd/201905/aec42560105843e9ac574ba7fe0a8c7e.shtml']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 2,
        },
        'FILES_STORE': os.path.join(__file__, '../data/file/'),  # 文件存储路径
        # 90 days of delay for files expiration
        'FILES_EXPIRES': 90,
    }

    def parse(self, response):
        url = response.urljoin(response.xpath('//div[@id="content"]//a/@href').extract_first())
        item = MyFileItem()
        item['file_urls'] = [url]  # must a list
        yield item
