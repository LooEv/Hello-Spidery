#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : keyword_filter.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-30 18:14:39
@History :
@Desc    : 
"""

import json
import re
import attr

from scrapy.http import Request
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class KeywordCheckMethodEnum:
    IN_CHECKING = 0
    RE_CHECKING = 1


class KeywordCheckScopeEnum:
    BODY = 0
    URL = 1
    HEADER = 2


@attr.s
class Keyword:
    """config format:
        {
            'keyword': some_keyword
            'check_method': KeywordCheckMethodEnum.IN_CHECKING,
            'scope': KeywordCheckScopeEnum.BODY,
            'allow': True or False,
            'change_proxy': True or False,
        }
    """
    keyword = attr.ib()
    check_method = attr.ib()
    check_scope = attr.ib()
    allow = attr.ib()
    change_proxy = attr.ib(default=False)

    def check(self, response):
        if self.check_scope == KeywordCheckScopeEnum.BODY:
            content = response.text
        elif self.check_scope == KeywordCheckScopeEnum.URL:
            content = response.url
        elif self.check_scope == KeywordCheckScopeEnum.HEADER:
            content = json.dumps(response.header)
        else:
            raise ValueError(f'keyword check scope: {self.check_scope} not supported')

        if self.check_method == KeywordCheckMethodEnum.IN_CHECKING:
            check_result = self.keyword in content
        elif self.check_method == KeywordCheckMethodEnum.RE_CHECKING:
            check_result = True if re.search(self.keyword, content) else False
        else:
            raise ValueError(f'keyword check method: {self.check_method} not supported')

        if check_result and not self.allow:
            return True, self.change_proxy
        else:
            return False, False


class KeywordFilterMiddleware(RetryMiddleware):

    def __init__(self, settings):
        super().__init__(settings)
        kw_filter_config_list = settings.getlist('KEYWORD_FILTER')
        self._kw_list = [Keyword(**kw_config) for kw_config in kw_filter_config_list]

    def process_response(self, request, response, spider):
        if not self._kw_list:
            return response

        is_filter = change_proxy = False
        reason = f"keyword filter by "
        for kw in self._kw_list:
            check_result, _change_proxy = kw.check(response)
            if check_result:
                reason += kw.keyword + " && "
                is_filter = True
            if _change_proxy:
                change_proxy = True

        if is_filter:
            result = self._retry(request, reason[:-4], spider)
            if isinstance(result, Request):
                result.meta['change_proxy'] = change_proxy
                return result
        return response
