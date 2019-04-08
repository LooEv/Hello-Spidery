#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : add_cookie.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-04 18:56:20
@History :
@Desc    : 
"""

from scrapy.exceptions import IgnoreRequest

__all__ = ["GiveSomeCookies"]


class GiveSomeCookies:
    def __init__(self, settings):
        cookie_provider_dict = settings.getdict('COOKIE_PROVIDER')
        if cookie_provider_dict:
            cls = cookie_provider_dict['class']
            args = cookie_provider_dict.get('args', ())
            kwargs = cookie_provider_dict.get('kwargs', {})
            self._cookie_provider = cls(*args, **kwargs)
        else:
            self._cookie_provider = None

    @classmethod
    def from_crawler(cls, crawler):
        d_mw = cls(crawler.settings)
        return d_mw

    def process_request(self, request, spider):
        if request.meta.get('inject_cookie_by_mw') or spider.settings.getbool('INJECT_COOKIE_BY_MW'):
            if not self._cookie_provider:
                raise AttributeError('injecting cookie by middleware needs cookie provider')
            cookie = self._cookie_provider.get_cookie()
            if cookie and isinstance(cookie, dict):
                request.cookies.update(cookie)
            else:
                raise IgnoreRequest(f'get wrong cookie: {cookie}')
