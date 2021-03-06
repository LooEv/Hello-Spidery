#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : retry.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-31 11:10:55
@History :
@Desc    : retry middleware
"""

import logging

from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import NotConfigured
from scrapy.utils.python import global_object_name
from scrapy.utils.response import response_status_message

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

logger = logging.getLogger(__name__)


class CustomRetryMiddleware:
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # retry when response's content is empty, response's status is 200
        # and request meta set empty_body False
        empty_body = request.meta.get('empty_body', False)
        if not empty_body and not response.body and response.status == 200:
            reason = '200 empty_response_body'
            return self._retry(request, reason, spider) or response
        return response

    def _retry(self, request, reason, spider):
        """modified logger level"""
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.info("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                        {'request': request, 'retries': retries, 'reason': reason},
                        extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.meta['change_proxy'] = True  # if use proxy, change proxy
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.warning("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                           {'request': request, 'retries': retries, 'reason': reason},
                           extra={'spider': spider})
