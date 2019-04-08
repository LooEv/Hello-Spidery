#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : github.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-29 22:20:32
@History :
@Desc    : 
"""

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest, HtmlResponse
import attr


@attr.s
class Cookie:
    host = attr.ib()
    port = attr.ib()

    def get_cookie(self):
        return {'host': self.host, 'port': self.port}


class GithubSpider(CrawlSpider):
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = [
        'https://github.com/issues',
    ]
