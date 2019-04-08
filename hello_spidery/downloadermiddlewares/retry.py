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

from scrapy.downloadermiddlewares.retry import RetryMiddleware


class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        # retry when response's content is empty, response's status is 200
        # and request meta set empty_body False
        empty_body = request.meta.get('empty_body', False)
        if not empty_body and not response.body and response.status == 200:
            reason = '200 empty_response_body'
            return self._retry(request, reason, spider) or response
        return response
