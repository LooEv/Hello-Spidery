#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : seed_test_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-11 22:43:32
@History :
@Desc    : 
"""

from hello_spidery.utils.spiders.seed_spider import HelloSeedSpider

from scrapy.http import Request, FormRequest


class SeedSpider(HelloSeedSpider):
    name = 'seed_spider'
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'SEED_PROVIDER_CONFIG': {
            'seed_server_type': 'mongodb',
            'host': '127.0.0.1',
            'port': '27017',
            'db_name': 'seeds_for_spider',
        }
    }

    def make_request_from_seed(self, seed):
        return Request(url=f'http://httpbin.org/get?num={seed["num"]}')

    def start_requests(self):
        yield Request(f'http://httpbin.org/ip', callback=self.parse)

    def parse(self, response):
        print(response.text)
