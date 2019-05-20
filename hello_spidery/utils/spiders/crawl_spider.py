#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : crawl_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-22 16:01:10
@History :
@Desc    : 
"""

from scrapy.spiders import CrawlSpider
from hello_spidery.utils.spiders.spider import HelloBaseSpider


class HelloCrawlSpider(HelloBaseSpider, CrawlSpider):
    name = 'hello_crawl_spider'
