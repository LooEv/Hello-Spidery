#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : default_error_back.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-05 21:03:12
@History :
@Desc    : 
"""

from types import MethodType
from scrapy import signals

__all__ = ["DefaultErrorBack"]


def default_err_back(spider, failure):
    _req = failure.request
    msg = 'request failed! URL: {}, METHOD: {}, request body: {}'
    if hasattr(spider, 'logger'):
        output = spider.logger.error
    else:
        output = print
    output('error_msg ==> ' + str(failure.value))
    output(msg.format(_req.url, _req.method, _req.body))


class DefaultErrorBack:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        use_default_err_back = spider.settings.getbool('USE_DEFAULT_ERROR_BACK')
        if use_default_err_back and not getattr(spider, 'default_err_back', None):
            spider.default_err_back = MethodType(default_err_back, spider)

    def process_request(self, request, spider):
        spider.logger.info(f'Crawling:[{request.method}]{request.url} {request.body[:50]}')
        if request.callback is None and getattr(spider, 'parse', None):
            request.callback = spider.parse
        if request.errback is None and spider.settings.getbool('USE_DEFAULT_ERROR_BACK'):
            request.errback = spider.default_err_back

    def process_response(self, request, response, spider):
        if response.status != 200:
            spider.logger.warning(f'Get non-200 response[{response.status}]:{request.url}')
        return response
